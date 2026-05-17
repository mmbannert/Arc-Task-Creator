classdef message
methods(Static)

function trialId = make_trial_id(blockId, phaseIndex, trialIndex)
    trialId = sprintf('%d_%d_%d', blockId, phaseIndex, trialIndex);
end

function print_block_prepare(b, nBlocks, block)
    fprintf('\n==============================\n');
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
        '%s [Block %d | %-11s | Trial %02d] ID=%s rule=%s resp=%s rt=%.3f correct=%s onset=%.3f\n', ...
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


function eyelink_trial_id(cfg, trialId)
    if cfg.eyelink_flag
        utilities.eyelink.msg('TRIALID %s', trialId);
    end
end


end
end