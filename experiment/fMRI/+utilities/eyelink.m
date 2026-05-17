classdef eyelink
methods(Static)

function el = setup(w, rect, dummyMode, participant)
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

    edfFile = utilities.eyelink.make_edf_name(participant);

    status = Eyelink('Openfile', edfFile);

    if status ~= 0
        error('Could not create EDF file: %s', edfFile);
    end

    if Eyelink('IsConnected') ~= 1 && ~dummyMode
        error('EyeLink is not connected.');
    end
end


function calibrate(el)
    EyelinkDoTrackerSetup(el);
end


function start_recording()
    Eyelink('Command', 'set_idle_mode');
    WaitSecs(0.05);

    Eyelink('StartRecording');
    WaitSecs(0.1);
end


function stop_recording()
    WaitSecs(0.1);
    Eyelink('StopRecording');
end


function msg(varargin)
    Eyelink('Message', varargin{:});
end


function close(participant, outDir)
    if isempty(outDir) || outDir == ""
        outDir = pwd;
    end

    edfFile = utilities.eyelink.make_edf_name(participant);

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


function emergency_shutdown()
    try
        Eyelink('StopRecording');
    end

    try
        Eyelink('CloseFile');
    end

    try
        Eyelink('Shutdown');
    end
end


function edfFile = make_edf_name(participant)
    p = char(string(participant));
    p = regexprep(p, '[^A-Za-z0-9]', '');

    if isempty(p)
        p = 'subj';
    end

    p = p(1:min(numel(p), 6));

    edfFile = [p '01'];
end

end
end