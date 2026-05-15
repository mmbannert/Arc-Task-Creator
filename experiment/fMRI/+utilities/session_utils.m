classdef session_utils
methods(Static)

function session = load_session(sessionPath)
    session = jsondecode(fileread(sessionPath));
    session = utilities.session_utils.normalize_session(session);
end


function session = normalize_session(session)
    session.blocks = utilities.session_utils.force_struct_array(session.blocks);

    for b = 1:numel(session.blocks)
        session.blocks(b).phases = utilities.session_utils.force_struct_array( ...
            session.blocks(b).phases);

        for ph = 1:numel(session.blocks(b).phases)
            P = session.blocks(b).phases(ph);

            if isfield(P, 'trials') && ~isempty(P.trials)
                session.blocks(b).phases(ph).trials = ...
                    utilities.session_utils.force_struct_array(P.trials);
            end

            if isfield(P, 'trial') && ~isempty(P.trial)
                session.blocks(b).phases(ph).trial = ...
                    utilities.session_utils.force_struct_array(P.trial);
            end
        end
    end
end


function a = force_struct_array(x)
    if isempty(x)
        a = x;
        return
    end

    if ~iscell(x)
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


function texCache = preload_textures(session, sessionPath, w)
    baseDir = fileparts(sessionPath);

    if baseDir == ""
        baseDir = pwd;
    end

    allImgs = utilities.session_utils.collect_all_images(session);

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
                    allImgs = [allImgs, utilities.session_utils.to_cellstr(tr0.imgs)]; %#ok<AGROW>
                end
            end

            if isfield(phase, 'trials') && ~isempty(phase.trials)
                for t = 1:numel(phase.trials)
                    tr = phase.trials(t);

                    if isfield(tr, 'imgs') && ~isempty(tr.imgs)
                        allImgs = [allImgs, utilities.session_utils.to_cellstr(tr.imgs)]; %#ok<AGROW>
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
        return
    end

    if ischar(x) || isstring(x)
        c = cellstr(x);
    elseif iscell(x)
        c = x;
    else
        c = cellstr(string(x));
    end
end

end
end