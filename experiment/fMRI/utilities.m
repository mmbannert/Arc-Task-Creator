classdef utilities
methods(Static)

% ===================== normalization =====================
function session = normalize_session(session)
    session.blocks = utilities.force_struct_array(session.blocks);

    for b = 1:numel(session.blocks)
        session.blocks(b).phases = utilities.force_struct_array(session.blocks(b).phases);

        for ph = 1:numel(session.blocks(b).phases)
            P = session.blocks(b).phases(ph);

            if isfield(P,'trials') && ~isempty(P.trials)
                session.blocks(b).phases(ph).trials = utilities.force_struct_array(P.trials);
            end

            if isfield(P,'trial') && ~isempty(P.trial)
                session.blocks(b).phases(ph).trial = utilities.force_struct_array(P.trial);
            end
        end
    end
end

function a = force_struct_array(x)
    % Convert jsondecode outputs (cell-of-struct with heterogeneous fields)
    % into a proper struct array by padding missing fields.

    if isempty(x)
        a = x;
        return
    end

    if ~iscell(x)
        a = x;  % already struct array (or something else)
        return
    end

    % If it's a cell but not structs, try best-effort:
    if ~all(cellfun(@isstruct, x))
        try
            a = [x{:}];
        catch
            a = x; % keep as cell if cannot concatenate
        end
        return
    end

    % Union of all fieldnames across elements
    allFields = {};
    for i = 1:numel(x)
        allFields = union(allFields, fieldnames(x{i}), 'stable');
    end

    % Create padded struct array
    a = repmat(cell2struct(repmat({[]}, 1, numel(allFields)), allFields, 2), 1, numel(x));

    for i = 1:numel(x)
        s = x{i};
        fn = fieldnames(s);
        for k = 1:numel(fn)
            a(i).(fn{k}) = s.(fn{k});
        end
    end
end

function c = to_cellstr(x)
    if isempty(x)
        c = {};
        return
    end
    if ischar(x) || isstring(x)
        c = cellstr(x);
    elseif iscell(x)
        c = x;
    else
        % best effort: struct array / other types shouldn't be here
        c = cellstr(string(x));
    end
end

% ===================== field getters =====================
function out = get_field_str(s, field)
    out = "";
    if isstruct(s) && isfield(s, field) && ~isempty(s.(field))
        out = string(s.(field));
    end
end

function out = get_field_strarr(s, field)
    out = strings(0,1);
    if isstruct(s) && isfield(s, field) && ~isempty(s.(field))
        out = string(s.(field));
    end
end

function out = get_field_numarr(s, field)
    out = [];
    if isstruct(s) && isfield(s, field) && ~isempty(s.(field))
        out = double(s.(field));
    end
end

function fam = trial_family(block, tr)
    if isfield(tr,'family') && ~isempty(tr.family)
        fam = string(tr.family);
    else
        fam = string(block.family);
    end
end

% ===================== logging =====================
function trialTemplate = trial_template()
    trialTemplate = struct( ...
        'block_id',[], ...
        'block_family',"", ...
        'trial_family',"", ...
        'phase',"", ...
        'phase_index',[], ...
        'trial_index',[], ...
        'bg',"", ...
        'hint',"", ...
        'tip',"", ...
        'rule',"", ...
        'ids',strings(0,1), ...
        'seeds',[], ...
        'imgs',strings(0,1), ...
        'correct',"", ...
        'resp',"", ...
        'is_correct',[], ...
        'rt',[], ...
        'stim_onset_abs',[], ...
        'stim_onset_rel',[] ...
    );
end

function trial = make_trial(trialTemplate, block, phase, ph, t, tr, resp, rt, tOn, t0)
    trial = trialTemplate;

    trial.block_id     = block.block_id;
    trial.block_family = string(block.family);
    trial.trial_family = utilities.trial_family(block, tr);

    trial.phase       = string(phase.phase);
    trial.phase_index = ph;
    trial.trial_index = t;

    trial.bg   = string(phase.bg);
    trial.hint = string(phase.hint);
    trial.tip  = string(phase.tip);

    trial.rule = utilities.get_field_str(tr, 'rule');
    trial.ids      = utilities.get_field_strarr(tr, 'ids');
    trial.seeds    = utilities.get_field_numarr(tr, 'seeds');
    trial.imgs     = utilities.get_field_strarr(tr, 'imgs');

    trial.correct    = utilities.get_field_str(tr, 'correct');
    trial.resp       = resp;
    trial.is_correct = utilities.score(resp, trial.correct);

    trial.rt = rt;
    trial.stim_onset_abs = tOn;
    trial.stim_onset_rel = tOn - t0;
end

function is_correct = score(resp, correct)
    is_correct = [];
    if correct == "same" || correct == "different"
        is_correct = (resp == correct);
    end
end

% ===================== preloading =====================
function allImgs = collect_all_images(session)
    allImgs = {};

    for b = 1:numel(session.blocks)
        block = session.blocks(b);

        for ph = 1:numel(block.phases)
            phase = block.phases(ph);

            if isfield(phase,'trial') && ~isempty(phase.trial)
                tr0 = phase.trial(1);
                if isfield(tr0,'imgs') && ~isempty(tr0.imgs)
                    allImgs = [allImgs, utilities.to_cellstr(tr0.imgs)]; %#ok<AGROW>
                end
            end

            if isfield(phase,'trials') && ~isempty(phase.trials)
                for t = 1:numel(phase.trials)
                    tr = phase.trials(t);
                    if isfield(tr,'imgs') && ~isempty(tr.imgs)
                        allImgs = [allImgs, utilities.to_cellstr(tr.imgs)]; %#ok<AGROW>
                    end
                end
            end
        end
    end

    allImgs = unique(allImgs, 'stable');
end

% ===================== UI helpers =====================
function rgb = phase_bg_rgb(bgName)
    luminosity = 0.4;  

    switch string(bgName)
        case "yellow"
            base_rgb = [1 1 0];
        case "cyan"
            base_rgb = [0 1 1];
        otherwise
            rgb = [0 0 0];
            return
    end

    % Convert to HSV, adjust luminosity, convert back to RGB
    hsv = rgb2hsv(base_rgb); 
    hsv(3) = luminosity; % hsv = [Hue, Saturation, Value]
    rgb = hsv2rgb(hsv); 
end

function [key, t] = wait_key(validKeys, escKey)
    KbReleaseWait; % debounce BEFORE

    while true
        [down, secs, kc] = KbCheck;
        if ~down
            continue
        end

        if kc(escKey)
            error('Experiment aborted (ESC).');
        end

        if any(kc(validKeys))
            key = find(kc, 1, 'first');
            t = secs;
            KbReleaseWait; % debounce AFTER
            return
        end
    end
end

% ===================== screens =====================
function [resp, rt, tOn] = twoimg_screen(w, rect, phase, tr, texCache, keySame, keyDiff, keyEsc)
    Screen('FillRect', w, [0.15 0.15 0.15]);

    frameColor = utilities.phase_bg_rgb(phase.bg);
    frameWidth = 30;
    Screen('FrameRect', w, frameColor, rect, frameWidth);

    utilities.draw_header(w, rect, phase);
    utilities.draw_two_stacked_imgs(w, rect, texCache, tr.imgs);

    tOn = Screen('Flip', w);

    [respKey, respTime] = utilities.wait_key([keySame keyDiff], keyEsc);
    rt = respTime - tOn;

    resp = "same";
    if respKey == keyDiff
        resp = "different";
    end
end

function draw_header(w, rect, phase)
    Screen('TextStyle', w, 1);
    Screen('TextSize', w, 38);
    DrawFormattedText(w, char(string(phase.hint)), 'center', rect(4)*0.12, [1 1 1]);
    Screen('TextStyle', w, 0);
    Screen('TextSize', w, 30);
    DrawFormattedText(w, char(string(phase.tip)), 'center', rect(4)*0.18, [1 1 1]);
end

function draw_two_stacked_imgs(w, rect, texCache, imgsField)
    imgs = utilities.to_cellstr(imgsField);
    if numel(imgs) < 2
        DrawFormattedText(w, '[need 2 imgs]', 'center', rect(4)*0.6, [1 1 1]);
        return
    end

    keyTop = char(imgs{1});
    keyBot = char(imgs{2});

    GAP = rect(4) * 0.06;
    wImg = rect(3) * 0.80;
    hImg = rect(4) * 0.30;

    topMargin = rect(4) * 0.22;
    bottomMargin = rect(4) * 0.06;

    availTop = topMargin;
    availBot = rect(4) - bottomMargin;

    stackH = 2*hImg + GAP;
    centerX = rect(3)/2;
    centerY = (availTop + availBot)/2;

    if stackH > (availBot - availTop)
        scale = (availBot - availTop) / stackH;
        hImg = hImg * scale;
        wImg = wImg * scale;
    end

    dstTop = CenterRectOnPointd([0 0 wImg hImg], centerX, centerY - (hImg/2 + GAP/2));
    dstBot = CenterRectOnPointd([0 0 wImg hImg], centerX, centerY + (hImg/2 + GAP/2));

    if isKey(texCache, keyTop)
        Screen('DrawTexture', w, texCache(keyTop), [], dstTop);
    else
        DrawFormattedText(w, '[missing top]', 'center', rect(4)*0.55, [1 1 1]);
    end

    if isKey(texCache, keyBot)
        Screen('DrawTexture', w, texCache(keyBot), [], dstBot);
    else
        DrawFormattedText(w, '[missing bottom]', 'center', rect(4)*0.80, [1 1 1]);
    end
end

% ===================== EyeLink =====================

function el = setup_eyelink(w, rect, dummyMode, participant)
    if ~EyelinkInit(dummyMode, 1)
        error('EyelinkInit failed.');
    end

    el = EyelinkInitDefaults(w);

    [~, vs] = Eyelink('GetTrackerVersion');
    fprintf('Running experiment on tracker: %s\n', vs);

    x0 = rect(1);
    y0 = rect(2);
    x1 = rect(3) - 1;
    y1 = rect(4) - 1;

    Eyelink('command', 'calibration_type = HV13');
    Eyelink('command', 'calibration_area_proportion = 0.41 0.41');
    Eyelink('command', 'validation_area_proportion = 0.41 0.41');

    Eyelink('command', 'file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE');
    Eyelink('command', 'file_sample_data = LEFT,RIGHT,GAZE,AREA');

    Eyelink('command', 'link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT');
    Eyelink('command', 'link_sample_data = LEFT,RIGHT,GAZE,AREA');

    Eyelink('command', 'screen_pixel_coords = %ld %ld %ld %ld', x0, y0, x1, y1);
    Eyelink('message', 'DISPLAY_COORDS %ld %ld %ld %ld', x0, y0, x1, y1);

    edfFile = utilities.make_edf_name(participant);

    status = Eyelink('Openfile', edfFile);
    if status ~= 0
        error('Could not create EDF file: %s', edfFile);
    end

    if Eyelink('IsConnected') ~= 1 && ~dummyMode
        error('EyeLink is not connected.');
    end
end


function calibrate_eyelink(el)
    EyelinkDoTrackerSetup(el);
end


function start_eyelink_recording()
    Eyelink('Command', 'set_idle_mode');
    WaitSecs(0.05);
    Eyelink('StartRecording');
    WaitSecs(0.1);
end


function stop_eyelink_recording()
    WaitSecs(0.1);
    Eyelink('StopRecording');
end


function msg_eyelink(varargin)
    Eyelink('Message', varargin{:});
end


function close_eyelink(participant, outDir)
    edfFile = utilities.make_edf_name(participant);

    Eyelink('Command', 'set_idle_mode');
    WaitSecs(0.05);
    Eyelink('CloseFile');

    try
        fprintf('Receiving EDF file: %s.edf\n', edfFile);
        Eyelink('ReceiveFile', [edfFile '.edf'], outDir, 1);
    catch
        warning('Could not receive EDF file.');
    end

    Eyelink('Shutdown');
end


function edfFile = make_edf_name(participant)
    % EDF filename should be max 8 chars before .edf
    p = char(string(participant));
    p = regexprep(p, '[^A-Za-z0-9]', '');

    if isempty(p)
        p = 'subj';
    end

    p = p(1:min(numel(p), 6));
    edfFile = [p '01'];
end

end % methods
end % classdef
