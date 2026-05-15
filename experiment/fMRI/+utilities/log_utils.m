classdef log_utils
methods(Static)

function log = init_log(session)
    log = struct();
    log.participant = string(session.participant);
    log.started_at = datestr(now, 30);
    log.trials = repmat(utilities.log_utils.trial_template(), 0, 1);
end


function trialTemplate = trial_template()
    trialTemplate = struct( ...
        'uid', "", ...
        'block_id', [], ...
        'block_family', "", ...
        'trial_family', "", ...
        'phase', "", ...
        'phase_index', [], ...
        'trial_index', [], ...
        'bg', "", ...
        'hint', "", ...
        'tip', "", ...
        'rule', "", ...
        'ids', strings(0, 1), ...
        'seeds', [], ...
        'imgs', strings(0, 1), ...
        'correct', "", ...
        'resp', "", ...
        'is_correct', [], ...
        'rt', [], ...
        'stim_onset_abs', [], ...
        'stim_onset_rel', [], ...
        'raw_trial', [] ...
    );
end


function trial = make_trial(block, phase, ph, t, tr, resp, rt, tOn, t0)
    trial = utilities.log_utils.trial_template();

    trial.block_id = block.block_id;
    trial.block_family = string(block.family);
    trial.trial_family = utilities.log_utils.trial_family(block, tr);
    trial.uid = sprintf('%d_%d_%d', block.block_id, ph, t);

    trial.phase = string(phase.phase);
    trial.phase_index = ph;
    trial.trial_index = t;

    trial.bg = utilities.log_utils.get_field_str(phase, 'bg');
    trial.hint = utilities.log_utils.get_field_str(phase, 'hint');
    trial.tip = utilities.log_utils.get_field_str(phase, 'tip');

    trial.rule = utilities.log_utils.get_field_str(tr, 'rule');

    trial.ids = utilities.log_utils.get_stimulus_ids(tr);
    trial.seeds = utilities.log_utils.get_stimulus_seeds(tr);
    trial.imgs = utilities.log_utils.get_field_strarr(tr, 'imgs');

    trial.correct = utilities.log_utils.get_field_str(tr, 'correct');
    trial.resp = string(resp);
    trial.is_correct = utilities.log_utils.score(trial.resp, trial.correct);

    trial.rt = rt;
    trial.stim_onset_abs = tOn;
    trial.stim_onset_rel = tOn - t0;

    trial.raw_trial = tr;
end


function fam = trial_family(block, tr)
    if isstruct(tr) && isfield(tr, 'family') && ~isempty(tr.family)
        fam = string(tr.family);
    else
        fam = string(block.family);
    end
end


function is_correct = score(resp, correct)
    is_correct = [];

    if correct == "same" || correct == "different"
        is_correct = (resp == correct);
    end
end


function out = get_field_str(s, field)
    out = "";

    if isstruct(s) && isfield(s, field) && ~isempty(s.(field))
        out = string(s.(field));
    end
end


function out = get_field_strarr(s, field)
    out = strings(0, 1);

    if isstruct(s) && isfield(s, field) && ~isempty(s.(field))
        out = string(s.(field));
    end
end


function ids = get_stimulus_ids(tr)
    ids = strings(0, 1);

    if ~isstruct(tr) || ~isfield(tr, 'stimuli') || isempty(tr.stimuli)
        return
    end

    stim = utilities.session_utils.force_struct_array(tr.stimuli);
    ids = strings(numel(stim), 1);

    for i = 1:numel(stim)
        ids(i) = utilities.log_utils.get_field_str(stim(i), 'id');
    end
end


function seeds = get_stimulus_seeds(tr)
    seeds = [];

    if ~isstruct(tr) || ~isfield(tr, 'stimuli') || isempty(tr.stimuli)
        return
    end

    stim = utilities.session_utils.force_struct_array(tr.stimuli);
    seeds = nan(numel(stim), 1);

    for i = 1:numel(stim)
        if isfield(stim(i), 'seed') && ~isempty(stim(i).seed)
            seeds(i) = double(stim(i).seed);
        end
    end
end


function print_trial(trial)

    correctStr = "NA";

    if ~isempty(trial.is_correct)
        correctStr = string(trial.is_correct);
    end

    fprintf( ...
        '[Block %d | %-11s | Trial %02d] ID=%s rule=%s resp=%s rt=%.3f correct=%s onset=%.3f\n', ...
        trial.block_id, ...
        string(trial.phase), ...
        trial.trial_index, ...
        trial.uid, ...
        string(trial.rule), ...
        string(trial.resp), ...
        trial.rt, ...
        correctStr, ...
        trial.stim_onset_rel);
end


function save_log(log, sessionPath, session)
    baseDir = fileparts(sessionPath);

    if baseDir == ""
        baseDir = pwd;
    end

    outName = sprintf('log_%s_%s.mat', ...
        string(session.participant), datestr(now, 30));

    outPath = fullfile(baseDir, outName);

    save(outPath, 'log');

    fprintf('Saved log: %s\n', outPath);
end

end
end