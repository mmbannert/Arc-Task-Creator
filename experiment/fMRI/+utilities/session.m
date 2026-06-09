classdef session
methods(Static)

function config = default_config()
    config = struct();

    % ---- general config ----
    config.SKIP_SYNC_TESTS = 1; % 1 in production
    config.REST_TIME = 1; % 10 in production 
    config.RESPONSE_TIME_LIMIT = 1; % 10 in production

    % ---- screen config ----
    config.use_windowed_mode = false;  % false in production
    config.window_rect = [100 100 900 900]; % [X_start Y_start X_end Y_end]
    config.resolution = [1400 1400];
    config.bg_color = [25 25 25]; % for grayish background

    % ---- response keys ----
    config.keys.same      = '3#'; % left button, carefull MPI keyboard has it reversed
    config.keys.different = '4$'; % right button

    % ---- EyeLink config ----
    config.eyelink_flag = 0;  % 1 in production

    % ---- scanner config ----
    config.use_scanner_trigger = true;
    config.trigger_key_name = 'w';
    config.TR = 2.0;
    config.dummy_seconds = 10;
    config.n_dummies = ceil(config.dummy_seconds / config.TR);
end


function keys = setup_keys(config)
    KbName('UnifyKeyNames');
 
    keys.sameResponse      = KbName(config.keys.same);
    keys.differentResponse = KbName(config.keys.different);
    keys.escape            = KbName('ESCAPE');
    keys.scannerTrigger    = KbName(config.trigger_key_name);
    keys.response          = [keys.sameResponse keys.differentResponse];
end


function session = load_session(sessionPath)
    session = jsondecode(fileread(sessionPath));
    session = utilities.session.normalize_session(session);
end


function session = normalize_session(session)
    session.blocks = utilities.session.force_struct_array(session.blocks);

    for b = 1:numel(session.blocks)
        session.blocks(b).phases = utilities.session.force_struct_array( ...
            session.blocks(b).phases);

        for ph = 1:numel(session.blocks(b).phases)
            P = session.blocks(b).phases(ph);

            if isfield(P, 'trials') && ~isempty(P.trials)
                session.blocks(b).phases(ph).trials = ...
                    utilities.session.force_struct_array(P.trials);
            end

            if isfield(P, 'trial') && ~isempty(P.trial)
                session.blocks(b).phases(ph).trial = ...
                    utilities.session.force_struct_array(P.trial);
            end
        end
    end
end


function texCache = preload_textures(session, sessionPath, w)
    baseDir = fileparts(sessionPath);

    if baseDir == ""
        baseDir = pwd;
    end

    allImgs = utilities.session.collect_all_images(session);
    texCache = containers.Map();

    fprintf('Preloading %d images...\n', numel(allImgs));

    for i = 1:numel(allImgs)
        rel = char(allImgs{i});
        p = fullfile(baseDir, rel);

        if ~isfile(p)
            error('Image file not found: %s', p);
        end

        im = imread(p);
        texCache(rel) = Screen('MakeTexture', w, im);
    end

    fprintf('Image preloading finished.\n');
end


function allImgs = collect_all_images(session)
    allImgs = {};

    for b = 1:numel(session.blocks)
        block = session.blocks(b);

        for ph = 1:numel(block.phases)
            phase = block.phases(ph);

            if isfield(phase, 'trial') && ~isempty(phase.trial)
                tr0 = phase.trial(1);

                if isfield(tr0, 'imgs') && ~isempty(tr0.imgs)
                    allImgs = [allImgs, utilities.session.to_cellstr(tr0.imgs)]; %#ok<AGROW>
                end
            end

            if isfield(phase, 'trials') && ~isempty(phase.trials)
                for t = 1:numel(phase.trials)
                    tr = phase.trials(t);

                    if isfield(tr, 'imgs') && ~isempty(tr.imgs)
                        allImgs = [allImgs, utilities.session.to_cellstr(tr.imgs)]; %#ok<AGROW>
                    end
                end
            end
        end
    end

    allImgs = unique(allImgs, 'stable');
end


function c = to_cellstr(x)
    if isempty(x)
        c = {};
    elseif iscell(x)
        c = x;
    else
        c = cellstr(string(x));
    end
end


function a = force_struct_array(x)
    if isempty(x) || ~iscell(x)
        a = x;
        return
    end

    if ~all(cellfun(@isstruct, x))
        try
            a = [x{:}];
        catch
            a = x;
        end
        return
    end

    allFields = {};
    for i = 1:numel(x)
        allFields = union(allFields, fieldnames(x{i}), 'stable');
    end

    emptyStruct = cell2struct(repmat({[]}, 1, numel(allFields)), allFields, 2);
    a = repmat(emptyStruct, 1, numel(x));

    for i = 1:numel(x)
        s = x{i};
        fn = fieldnames(s);

        for k = 1:numel(fn)
            a(i).(fn{k}) = s.(fn{k});
        end
    end
end

end
end