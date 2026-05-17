function run_experiment(sessionPath)
% Run by calling: run_experiment("session.json")

config = utilities.session.default_config();
% Change configurations in utilities.session

try
    session = utilities.session.load_session(sessionPath);
    keys = utilities.session.setup_keys(session, config);
    [window, windowRect] = utilities.screen.setup_window(config);

    textureCache = utilities.session.preload_textures(session, sessionPath, window);
    experimentLog = utilities.log.init_log(session);

    experimentStartTime = prepare_experiment(window, windowRect, session, keys, config);

    for blockIndex = 1:numel(session.blocks)
        block = session.blocks(blockIndex);
    
        utilities.message.print_block_prepare(blockIndex, numel(session.blocks), block);
        utilities.screen.block_progress_screen(window, windowRect, blockIndex, numel(session.blocks));
    
        blockTrials = run_block(window, windowRect, block, textureCache, keys, config, experimentStartTime);
        experimentLog.trials = [experimentLog.trials; blockTrials]; %#ok<AGROW>

        blockSummary = utilities.log.summarize_trials(blockTrials);
        utilities.message.print_block_summary(blockIndex, blockSummary);
        utilities.screen.block_score_screen(window, blockSummary);

    end

    utilities.log.save_log(experimentLog, sessionPath, session);

    if config.eyelink_flag
        fprintf('[EyeLink] Stopping recording...\n');
        utilities.eyelink.stop_recording();
        utilities.eyelink.close(session.participant, fileparts(sessionPath));
    end

    Screen('CloseAll');
    fprintf('\nExperiment finished successfully.\n');

catch errorInfo
    utilities.eyelink.emergency_shutdown();
    try Screen('CloseAll'); end %#ok<TRYNC>
    rethrow(errorInfo);
end

end


% ========================================================================
% Local experiment-flow functions
% ========================================================================


function blockTrials = run_block(window, windowRect, block, textureCache, keys, config, scanStartTime)

trialTemplate = utilities.log.trial_template();
blockTrials = repmat(trialTemplate, 0, 1);

for phaseIndex = 1:numel(block.phases)
    phase = block.phases(phaseIndex);

    if string(phase.phase) == "phase_start"
        
        if phaseIndex > 1 % Therefore just before rule memorization 
            utilities.screen.fixation_screen(window, windowRect, config.REST_TIME); end

        trial = run_phase_start( ...
            window, windowRect, block, phase, phaseIndex, textureCache, keys, config, scanStartTime);

        blockTrials(end+1, 1) = trial; %#ok<AGROW>
        utilities.message.print_trial(trial);
        continue
    end

    phaseTrials = run_decision_phase( ...
        window, windowRect, block, phase, phaseIndex, textureCache, keys, config, scanStartTime);

    blockTrials = [blockTrials; phaseTrials]; %#ok<AGROW>
end

utilities.screen.fixation_screen(window, windowRect, config.REST_TIME);
end


function trial = run_phase_start( ...
    window, windowRect, block, phase, phaseIndex, textureCache, keys, config, experimentStartTime)

phaseStartTrial = phase.trial(1);

trialId = utilities.message.make_trial_id(block.block_id, phaseIndex, 0);
utilities.message.eyelink_trial_id(config, trialId);

[response, reactionTime, stimulusOnsetTime] = utilities.screen.rule_start_screen( ...
    window, windowRect, phase, phaseStartTrial, textureCache, keys.response, keys.escape);

trial = utilities.log.make_trial( ...
    block, phase, phaseIndex, 0, phaseStartTrial, ...
    response, reactionTime, stimulusOnsetTime, experimentStartTime);

end


function phaseTrials = run_decision_phase( ...
    window, windowRect, block, phase, phaseIndex, textureCache, keys, config, experimentStartTime)

trialTemplate = utilities.log.trial_template();
phaseTrials = repmat(trialTemplate, 0, 1);

for trialIndex = 1:numel(phase.trials)
    trialData = phase.trials(trialIndex);

    trialId = utilities.message.make_trial_id(block.block_id, phaseIndex, trialIndex);
    utilities.message.eyelink_trial_id(config, trialId);

    [response, reactionTime, stimulusOnsetTime, allResponses, allReactionTimes] = ...
        utilities.screen.decision_screen( ...
            window, windowRect, phase, trialData, textureCache, ...
            keys.sameResponse, keys.differentResponse, keys.escape, ...
            config.DECISION_TIME_LIMIT);

    trial = utilities.log.make_trial( ...
        block, phase, phaseIndex, trialIndex, trialData, ...
        response, reactionTime, stimulusOnsetTime, experimentStartTime, ...
        allResponses, allReactionTimes);

    phaseTrials(end+1, 1) = trial; %#ok<AGROW>
    utilities.message.print_trial(trial);
end

end


function experimentStartTime = prepare_experiment(window, windowRect, session, keys, config)

fprintf('\n==============================\n');
fprintf('Experiment setup\n');
fprintf('Participant: %s\n', string(session.participant));
fprintf('==============================\n');

utilities.screen.message_screen( ...
    window, windowRect, ...
    sprintf(['Experiment setup' ...
             'Press any response button when ready.']));

if config.eyelink_flag
    fprintf('[EyeLink] Opening connection...\n');

    eyelinkDefaults = utilities.eyelink.setup( ...
        window, windowRect, config.DUMMY_MODE, session.participant);

    fprintf('[EyeLink] Calibration screen active. Complete calibration on tracker PC.\n');
    utilities.eyelink.calibrate(eyelinkDefaults);

    fprintf('[EyeLink] Starting recording...\n');
    utilities.eyelink.start_recording();

    utilities.screen.message_screen( ...
    window, windowRect, ...
    sprintf(['Eye tracker calibration is complete.\n\n' ...
             'Press any response button when ready for the scan.']));
else
    utilities.screen.message_screen( ...
    window, windowRect, ...
    sprintf(['Eye tracker calibration is disabled.\n\n' ...
             'Press any response button when ready for the scan.']));

    fprintf('[EyeLink] Disabled.\n');
end

fprintf('[Participant] Waiting for readiness button press...\n');
utilities.screen.wait_key(keys.response, keys.escape);
fprintf('[Participant] Ready.\n');

utilities.screen.message_screen( ...
    window, windowRect, ...
    'Waiting for scanner...');

fprintf('[Scanner] Waiting for trigger key "%s"...\n', config.trigger_key_name);

if config.use_scanner_trigger
    [~, experimentStartTime] = utilities.screen.wait_key( ...
        keys.scannerTrigger, keys.escape);
else
    experimentStartTime = GetSecs();
end

fprintf('[Scanner] First trigger received.\n');
fprintf('[Experiment] Start time: %.4f\n\n', experimentStartTime);

if config.eyelink_flag
    utilities.eyelink.msg('EXPERIMENT_START %.4f', experimentStartTime);
end

end

