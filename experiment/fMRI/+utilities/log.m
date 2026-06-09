classdef log
methods(Static)

function log = init_log(session,config)
    log = struct();

    log.participant = string(session.participant);
    log.started_at = string(datetime("now", "Format", "yyyyMMdd'T'HHmmss"));

    log.session = struct();
    log.session.seed = session.seed;
    log.session.number_of_decision_trials_per_phase = session.number_of_decision_trials_per_phase;
    log.session.number_of_trials_per_block = session.number_of_trials_per_block;
    log.session.number_of_family_blocks = session.number_of_family_blocks;
    log.session.number_of_mix_blocks = session.number_of_mix_blocks;
    log.session.number_of_trials_total = session.number_of_trials_total;
    log.session.keys = config.keys;

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
        'stim_onset_rel', [], ...
        'stimulus_info', [] ...
    );
end


function trial = make_trial( ...
    block, phase, phaseIndex, trialIndex, ...
    trialData, response, reactionTime, stimulusOnsetTime, experimentStartTime, ...
    allResponses, allReactionTimes)

    trial = utilities.log.trial_template();

    trial.block_id = block.block_id;
    trial.block_family = string(block.family);
    trial.trial_family = utilities.log.trial_family(block, trialData);
    trial.uid = utilities.log.make_trial_id(block.block_id, phaseIndex, trialIndex);

    trial.phase = string(phase.phase);
    trial.phase_index = phaseIndex;
    trial.trial_index = trialIndex;

    trial.bg = utilities.log.get_field_str(phase, 'bg');
    trial.rule = utilities.log.get_field_str(trialData, 'rule');
    trial.imgs = utilities.log.get_field_strarr(trialData, 'imgs');
    trial.correct = utilities.log.get_field_str(trialData, 'correct');

    trial.resp = utilities.log.normalize_response(phase, string(response));
    trial.all_responses = utilities.log.normalize_responses(phase, allResponses);    trial.all_rts = allReactionTimes;
    trial.rt = reactionTime;
    trial.is_correct = utilities.log.score(trial.resp, trial.correct);

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
        string(session.participant), ...
        string(datetime("now", "Format", "yyyyMMdd'T'HHmmss")));

    outPath = fullfile(baseDir, outName);
    save(outPath, 'log');
    fprintf('Saved log: %s\n', outPath);
end

function trialId = make_trial_id(blockId, phaseIndex, trialIndex)
    trialId = sprintf('%d_%d_%d', blockId, phaseIndex, trialIndex);
end


function resp = normalize_response(phase, resp)
    phaseName = string(phase.phase);

    if resp == "timeout"
        return
    end

    switch phaseName
        case "inference_start",    resp = "ready";
        case "application_start",  resp = "memorized";
    end
end

function responses = normalize_responses(phase, responses)
    for i = 1:numel(responses)
        responses(i) = utilities.log.normalize_response(phase, responses(i));
    end
end


function print_block_prepare(b, nBlocks, block)
    fprintf('==============================\n');
    fprintf('Preparing block %d / %d | family: %s\n', ...
        b, nBlocks, string(block.family));
    fprintf('==============================\n');
end


function print_trial(trial)
    if isempty(trial.is_correct)
        correctStr = 'NA';
        marker = '   ';
    elseif trial.is_correct
        correctStr = 'true';
        marker = '   ';
    else
        correctStr = 'FALSE';
        marker = ' ! ';
    end

    fprintf( ...
        '%s [Block %d | %-17s | Trial %02d] ID=%s rule=%s resp=%s rt=%.3f correct=%s onset=%.3f\n', ...
        marker, ...
        trial.block_id, ...
        char(string(trial.phase)), ...
        trial.trial_index, ...
        char(trial.uid), ...
        char(string(trial.rule)), ...
        char(string(trial.resp)), ...
        trial.rt, ...
        correctStr, ...
        trial.stim_onset_rel);
end


function print_block_summary(blockIndex, summary)
    fprintf('\n[Block %d summary]\n', blockIndex);
    fprintf('Trials:   %d decision trials\n', summary.decisionCount);
    fprintf('Correct:  %d\n', summary.correctCount);
    fprintf('Accuracy: %.1f%%\n', summary.accuracyPercent);
    fprintf('Mean RT:  %.3f s\n\n', summary.meanRt);
end

end
end