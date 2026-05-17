classdef log
methods(Static)

function log = init_log(session)
    log = struct();
    log.participant = string(session.participant);
    log.started_at = datestr(now, 30);
    log.trials = repmat(utilities.log.trial_template(), 0, 1);
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
        'rule', "", ...
        'imgs', strings(0, 1), ...
        'correct', "", ...
        'resp', "", ...
        'is_correct', [], ...
        'rt', [], ...
        'all_responses', strings(0, 1), ...
        'all_rts', [], ...
        'stim_onset_abs', [], ...
        'stim_onset_rel', [], ...
        'stimulus_info', [] ...
    );
end


function trial = make_trial( ...
    block, phase, phaseIndex, trialIndex, ...
    trialData, response, reactionTime, stimulusOnsetTime, experimentStartTime, ...
    allResponses, allReactionTimes)

    if nargin < 10
        allResponses = strings(0, 1);
        allReactionTimes = [];
    end

    trial = utilities.log.trial_template();

    trial.block_id = block.block_id;
    trial.block_family = string(block.family);
    trial.trial_family = utilities.log.trial_family(block, trialData);
    trial.uid = utilities.message.make_trial_id(block.block_id, phaseIndex, trialIndex);

    trial.phase = string(phase.phase);
    trial.phase_index = phaseIndex;
    trial.trial_index = trialIndex;

    trial.bg = utilities.log.get_field_str(phase, 'bg');
    trial.rule = utilities.log.get_field_str(trialData, 'rule');
    trial.imgs = utilities.log.get_field_strarr(trialData, 'imgs');

    trial.correct = utilities.log.get_field_str(trialData, 'correct');
    trial.resp = string(response);
    trial.is_correct = utilities.log.score(trial.resp, trial.correct);

    trial.rt = reactionTime;
    trial.all_responses = allResponses;
    trial.all_rts = allReactionTimes;

    trial.stim_onset_abs = stimulusOnsetTime;
    trial.stim_onset_rel = stimulusOnsetTime - experimentStartTime;

    trial.stimulus_info = trialData;
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

    stim = utilities.session.force_struct_array(tr.stimuli);
    ids = strings(numel(stim), 1);

    for i = 1:numel(stim)
        ids(i) = utilities.log.get_field_str(stim(i), 'id');
    end
end


function seeds = get_stimulus_seeds(tr)
    seeds = [];

    if ~isstruct(tr) || ~isfield(tr, 'stimuli') || isempty(tr.stimuli)
        return
    end

    stim = utilities.session.force_struct_array(tr.stimuli);
    seeds = nan(numel(stim), 1);

    for i = 1:numel(stim)
        if isfield(stim(i), 'seed') && ~isempty(stim(i).seed)
            seeds(i) = double(stim(i).seed);
        end
    end
end

function summary = summarize_trials(trials)

    hasAnswer = arrayfun(@(trial) ~isempty(trial.is_correct), trials);

    decisionTrials = trials(hasAnswer);

    summary.decisionCount = numel(decisionTrials);

    if summary.decisionCount == 0
        summary.correctCount = 0;
        summary.accuracyPercent = NaN;
        summary.meanRt = NaN;
        return
    end

    correctness = [decisionTrials.is_correct];
    reactionTimes = [decisionTrials.rt];

    summary.correctCount = sum(correctness);
    summary.accuracyPercent = 100 * summary.correctCount / summary.decisionCount;
    summary.meanRt = mean(reactionTimes, 'omitnan');

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