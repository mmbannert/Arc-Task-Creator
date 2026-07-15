function scanPlan = compute_scan_plan(session)

cfg = utilities.session.default_config();

    sessionText = fileread(session);
        session = jsondecode(sessionText);

    experimentDuration = ...
        session.number_of_trials_total * cfg.response_time_window + ... % all trials
        session.number_of_blocks * cfg.rest_time; % all rest

    totalDuration = cfg.dummy_seconds + experimentDuration + cfg.rest_time;

    scanPlan.experiment_duration = experimentDuration;
    scanPlan.total_duration = totalDuration;
    scanPlan.n_TRs = ceil(totalDuration / cfg.TR);
    scanPlan.TR = cfg.TR;

    fprintf('Required scan duration: %.1f seconds\n', scanPlan.total_duration);
    fprintf('Required TRs/volumes: %d\n', scanPlan.n_TRs);
end