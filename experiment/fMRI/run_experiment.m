function run_experiment(sessionPath)
% Run by calling: run_experiment("session.json")

SKIP_SYNC_TESTS = 1;

eyelink_flag = 0;
DUMMY_MODE = 1;

REST_TIME = 15;

try
    session = jsondecode(fileread(sessionPath));
    session = utilities.normalize_session(session);

    % ---- keys from session.json ----
    KbName('UnifyKeyNames');
    keySame = KbName(char(session.keys.same));
    keyDiff = KbName(char(session.keys.different));
    keyEsc  = KbName('ESCAPE');

    % ---- window ----
    Screen('Preference','SkipSyncTests', SKIP_SYNC_TESTS);
    AssertOpenGL;
    PsychImaging('PrepareConfiguration')

    screen_id = max(Screen('Screens')); % usually the peripherial screen has max id
    resolution = [1400 1400];
    PsychImaging('AddTask', 'General', 'UsePanelFitter', resolution, 'Aspect')
    [w, rect] = PsychImaging('OpenWindow', screen_id, [0 0 0]);

    Screen('ColorRange', w, 1);
    Screen('TextFont', w, 'Arial');

    baseDir = fileparts(sessionPath);
    if baseDir == "" % if empty make dir
        baseDir = pwd;
    end

    % ---- eye tracker ----
    if eyelink_flag
        el = utilities.setup_eyelink(w, rect, DUMMY_MODE, session.participant);
        utilities.calibrate_eyelink(el);
    end

    % ---- preload textures ----
    texCache = containers.Map();
    allImgs = utilities.collect_all_images(session);
    for i = 1:numel(allImgs)
        rel = char(allImgs{i});
        p = fullfile(baseDir, rel);

        im = imread(p);
        texCache(rel) = Screen('MakeTexture', w, im);
    end

    % ---- log init ----
    trialTemplate = utilities.trial_template();
    log = struct;
    log.participant = string(session.participant);
    log.started_at  = datestr(now,30);
    log.trials = repmat(trialTemplate, 0, 1);

    t0 = GetSecs();

    % ---- task loop ----
    for b = 1:numel(session.blocks)
        block = session.blocks(b);

        if eyelink_flag
            utilities.msg_eyelink('BLOCK_START %d FAMILY %s', ...
                b, char(string(block.family)));
            utilities.start_eyelink_recording();
        end

        for ph = 1:numel(block.phases)
            phase = block.phases(ph);
            phaseName = string(phase.phase);

            % ---------- phase_start: single trial stored in phase.trial ----------
            if phaseName == "phase_start"
                utilities.rest_screen(w, rect, REST_TIME, 'Take a short break.');

                if isfield(phase,'trial') && ~isempty(phase.trial)
                    tr0 = phase.trial(1);
                else
                    tr0 = struct;
                end

                trialId = sprintf('%d_%d_%d', b, ph, 0);

                if eyelink_flag
                    utilities.msg_eyelink('TRIALID %s', trialId);
                end

                [resp, rt, tOn] = utilities.twoimg_screen( ...
                    w, rect, phase, tr0, texCache, keySame, keyDiff, keyEsc);

                trial = utilities.make_trial( ...
                    trialTemplate, block, phase, ph, 0, tr0, resp, rt, tOn, t0);

                log.trials(end+1,1) = trial;
                continue
            end

            % ---------- inference/application: multiple trials in phase.trials ----------
            if ~isfield(phase,'trials') || isempty(phase.trials)
                continue
            end

            for t = 1:numel(phase.trials)
                tr = phase.trials(t);

                trialId = sprintf('%d_%d_%d', b, ph, t);

                if eyelink_flag
                    utilities.msg_eyelink('TRIALID %s', trialId);
                end

                [resp, rt, tOn] = utilities.twoimg_screen( ...
                    w, rect, phase, tr, texCache, keySame, keyDiff, keyEsc);

                trial = utilities.make_trial( ...
                    trialTemplate, block, phase, ph, t, tr, resp, rt, tOn, t0);

                log.trials(end+1,1) = trial; %#ok<AGROW>
            end
        end

        if eyelink_flag
            utilities.msg_eyelink('BLOCK_END %d', b);
            utilities.stop_eyelink_recording();
        end
    end

    % ---- save log and close all ----
    outName = sprintf('log_%s_%s.mat', string(session.participant), datestr(now,30));
    save(fullfile(baseDir, outName), 'log');

    if eyelink_flag
        utilities.close_eyelink(session.participant, baseDir);
    end
    Screen('CloseAll');

catch ME
    try
        if exist('eyelink_flag', 'var') && eyelink_flag
            Eyelink('StopRecording');
            Eyelink('CloseFile');
            Eyelink('Shutdown');
        end
    end
    try Screen('CloseAll'); end %#ok<TRYNC>
    rethrow(ME);
end
end