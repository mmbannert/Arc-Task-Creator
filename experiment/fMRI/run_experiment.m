function run_experiment(sessionPath)
% Run by calling:
%   run_experiment("session.json")

cfg = struct();

% ---- general config ----
cfg.SKIP_SYNC_TESTS = 1;
cfg.REST_TIME = 15;

% ---- screen config ----
cfg.use_windowed_mode = true;  % set false for scanner/fullscreen
cfg.window_rect = [100 100 900 900];
cfg.resolution = [1400 1400];
cfg.bg_color = [0 0 0];

% ---- EyeLink config ----
cfg.eyelink_flag = 0;
cfg.DUMMY_MODE = 1;

% ---- scanner config ----
cfg.use_scanner_trigger = true;
cfg.trigger_key_name = 'w';

try
    % ===================== load session =====================
    session = utilities.session_utils.load_session(sessionPath);

    % ===================== keys =====================
    KbName('UnifyKeyNames');

    keySame = KbName(char(session.keys.same));
    keyDiff = KbName(char(session.keys.different));
    keyEsc  = KbName('ESCAPE');
    keyTrigger = KbName(cfg.trigger_key_name);

    responseKeys = [keySame keyDiff];

    % ===================== window =====================
    [w, rect] = utilities.screen_utils.setup_window(cfg);

    % ===================== EyeLink =====================
    if cfg.eyelink_flag
        el = utilities.eyelink_utils.setup(w, rect, cfg.DUMMY_MODE, session.participant);
        utilities.eyelink_utils.calibrate(el);
    end

    % ===================== preload =====================
    texCache = utilities.session_utils.preload_textures(session, sessionPath, w);

    % ===================== log =====================
    log = utilities.log_utils.init_log(session);

    % ===================== task loop =====================
    fprintf('\nExperiment started for participant %s\n', string(session.participant));

    for b = 1:numel(session.blocks)
        block = session.blocks(b);

        fprintf('\n==============================\n');
        fprintf('Preparing block %d / %d | family: %s\n', ...
            b, numel(session.blocks), string(block.family));
        fprintf('==============================\n');

        % ---------- participant ready ----------
        utilities.screen_utils.message_screen( ...
            w, rect, ...
            sprintf('Block %d / %d\n\nPress any response button when ready for scan.', ...
            b, numel(session.blocks)));

        fprintf('Waiting for participant readiness...\n');
        utilities.screen_utils.wait_key(responseKeys, keyEsc);
        fprintf('Participant ready.\n');

        % ---------- wait for scanner trigger ----------
        utilities.screen_utils.message_screen(w, rect, 'Waiting for scanner...');
        fprintf('Waiting for scanner trigger key "%s"...\n', cfg.trigger_key_name);

        if cfg.use_scanner_trigger
            [~, scan_t0] = utilities.screen_utils.wait_key(keyTrigger, keyEsc);
        else
            scan_t0 = GetSecs();
        end

        fprintf('Scanner trigger received. Block %d started at %.4f\n', b, scan_t0);

        if cfg.eyelink_flag
            utilities.eyelink_utils.msg('BLOCK_START %d FAMILY %s', ...
                b, char(string(block.family)));
            utilities.eyelink_utils.start_recording();
        end

        % ---------- phases ----------
        for ph = 1:numel(block.phases)
            phase = block.phases(ph);
            phaseName = string(phase.phase);

            if phaseName == "phase_start"
                if ph > 1
                    utilities.screen_utils.fixation_screen( ...
                        w, rect, cfg.REST_TIME);
                end

                [trial, log] = run_phase_start( ...
                    w, rect, texCache, ...
                    block, phase, b, ph, ...
                    responseKeys, keyEsc, scan_t0, log, cfg);

                utilities.log_utils.print_trial(trial);

                continue
            end

            if ~isfield(phase, 'trials') || isempty(phase.trials)
                fprintf('Skipping empty phase: %s\n', phaseName);
                continue
            end

            for t = 1:numel(phase.trials)
                tr = phase.trials(t);

                trialId = sprintf('%d_%d_%d', b, ph, t);
                

                if cfg.eyelink_flag
                    utilities.eyelink_utils.msg('TRIALID %s', trialId);
                end

                [resp, rt, tOn] = utilities.screen_utils.twoimg_screen( ...
                    w, rect, phase, tr, texCache, keySame, keyDiff, keyEsc);

                trial = utilities.log_utils.make_trial( ...
                    block, phase, ph, t, tr, resp, rt, tOn, scan_t0);

                log.trials(end+1, 1) = trial; %#ok<AGROW>

                utilities.log_utils.print_trial(trial);
            end
        end

        if cfg.eyelink_flag
            utilities.eyelink_utils.msg('BLOCK_END %d', b);
            utilities.eyelink_utils.stop_recording();
        end
    end

    % ===================== finish =====================
    utilities.log_utils.save_log(log, sessionPath, session);

    if cfg.eyelink_flag
        utilities.eyelink_utils.close(session.participant, fileparts(sessionPath));
    end

    Screen('CloseAll');
    fprintf('\nExperiment finished successfully.\n');

catch ME
    utilities.eyelink_utils.emergency_shutdown();
    try Screen('CloseAll'); end %#ok<TRYNC>
    rethrow(ME);
end

end


function [trial, log] = run_phase_start( ...
    w, rect, texCache, ...
    block, phase, b, ph, ...
    responseKeys, keyEsc, scan_t0, log, cfg)

if isfield(phase, 'trial') && ~isempty(phase.trial)
    tr0 = phase.trial(1);
else
    tr0 = struct();
end

trialId = sprintf('%d_%d_%d', b, ph, 0);

if cfg.eyelink_flag
    utilities.eyelink_utils.msg('TRIALID %s', trialId);
end

[resp, rt, tOn] = utilities.screen_utils.rule_start_screen( ...
    w, rect, phase, tr0, texCache, responseKeys, keyEsc);

trial = utilities.log_utils.make_trial( ...
    block, phase, ph, 0, tr0, resp, rt, tOn, scan_t0);

log.trials(end+1, 1) = trial;

end