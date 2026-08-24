
classdef session
methods(Static)

function config = default_config()
    config = struct();

    % ---- general config ----
    config.skip_sync_tests = 0; % 0 in production
    config.rest_time = 1; % 10 in production
    config.response_time_window = 1; % 10 in production

    % ---- screen config ----
    config.use_windowed_mode = true;  % false in production
    config.window_rect = [50 50 1350 1350]; % [X_start Y_start X_end Y_end]
    config.resolution = [1300 1300];
    config.bg_color = [25 25 25]; % for grayish background
    
    % Native resolution of display device
    % config.native_resolution = [1920, 1080];     % in 3T lab
    % config.native_resolution = [1600, 1200];    % at desktop
    config.native_resolution = [3440, 1440];    % at brunsstr

    % ---- response keys ----
    config.keys.same      = '3#'; % left button. 
    config.keys.different = '4$'; % right button. 
    % 3T lab keyboard for RIGHT hand has '4$' on index finger (left-most button) and '3#' on middle finger (second-from-left button).
    % For standard keyboard swap them.

    % ---- EyeLink config ----
    config.eyelink_flag = 0;  % 1 in production

    % ---- scanner config ----
    config.use_scanner_trigger = false;
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
        im = imread(p);
        texCache(rel) = Screen('MakeTexture', w, im);
    end

    fprintf('Image preloading finished.\n');
end


function allImgs = collect_all_images(session)
    allImgs = {};

    for b = 1:numel(session.blocks)
        block = session.blocks(b);

        for t = 1:numel(block.trials)
            tr = block.trials(t);

            if isfield(tr, 'imgs') && ~isempty(tr.imgs)
                allImgs = [allImgs, utilities.session.to_cellstr(tr.imgs)]; %#ok<AGROW>
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


end
end