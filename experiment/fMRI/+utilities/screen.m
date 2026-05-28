classdef screen
methods(Static)

function [w, rect] = setup_window(config)
    Screen('Preference', 'SkipSyncTests', config.SKIP_SYNC_TESTS);
    Screen('Preference', 'Verbosity', config.verbosity);
    AssertOpenGL;

    PsychImaging('PrepareConfiguration');
    screenId = max(Screen('Screens'));
    PsychImaging('AddTask', 'General', 'UsePanelFitter', config.resolution, 'Aspect');

    if config.use_windowed_mode
        [w, rect] = PsychImaging('OpenWindow', screenId, config.bg_color, config.window_rect);
    else
        [w, rect] = PsychImaging('OpenWindow', screenId, config.bg_color);
    end

    Screen('ColorRange', w, 1);
    Screen('TextFont', w, 'Arial');

    fprintf('PTB window opened on screen %d.\n', screenId);
end


function [key, time] = wait_key(validKeys, escapeKey)
    KbReleaseWait;

    while true
        [isDown, keyTime, keyCode] = KbCheck;

        if ~isDown
            continue
        end

        if keyCode(escapeKey)
            error('Experiment aborted with ESC.');
        end

        if any(keyCode(validKeys))
            key = find(keyCode, 1, 'first');
            time = keyTime;
            KbReleaseWait;
            return
        end
    end
end


function text_screen(w, text, duration, fontSize, isBold)
    if nargin < 5
        isBold = false;
    end

    if nargin < 4
        fontSize = 34;
    end

    if nargin < 3
        duration = [];
    end

    utilities.screen.clear_screen(w);

    Screen('TextStyle', w, double(isBold));
    Screen('TextSize', w, fontSize);

    DrawFormattedText(w, char(string(text)), 'center', 'center', [1 1 1]);

    flipTime = Screen('Flip', w);

    if ~isempty(duration)
        WaitSecs('UntilTime', flipTime + duration);
    end
end


function message_screen(w, rect, text) %#ok<INUSD>
    utilities.screen.text_screen(w, text, [], 34, false);
end

function fixation_screen(w, rect, seconds)
    utilities.screen.clear_screen(w);

    crossColor = [1 1 1];
    crossSize = 20;
    lineWidth = 4;

    xCenter = rect(3) / 2;
    yCenter = rect(4) / 2;

    Screen('DrawLine', w, crossColor, ...
        xCenter - crossSize, yCenter, ...
        xCenter + crossSize, yCenter, lineWidth);

    Screen('DrawLine', w, crossColor, ...
        xCenter, yCenter - crossSize, ...
        xCenter, yCenter + crossSize, lineWidth);

    flipTime = Screen('Flip', w);
    WaitSecs('UntilTime', flipTime + seconds);
end

function scannerSync = scanner_sync_screen( ...
    window, windowRect, scannerTriggerKey, escapeKey, config)

    numberOfDummyTriggers = config.n_dummies;

    scannerSync.TR = config.TR;
    scannerSync.n_dummies = numberOfDummyTriggers;

    scannerSync.trigger_times_abs = ...
        nan(numberOfDummyTriggers + 1, 1);

    if config.wait_for_experimenter_trigger
        utilities.screen.message_screen(window, windowRect, 'Waiting for experimenter...');
        fprintf('[Scanner] Waiting for experimenter trigger...\n');
        utilities.screen.wait_key(scannerTriggerKey, escapeKey);
    end

    utilities.screen.fixation_screen(window, windowRect, 0);

    fprintf('[Scanner] Waiting for %d dummy triggers...\n', ...
        numberOfDummyTriggers);

    for triggerIndex = 1:(numberOfDummyTriggers + 1)

        [~, triggerTime] = utilities.screen.wait_key( ...
            scannerTriggerKey, escapeKey);

        scannerSync.trigger_times_abs(triggerIndex) = triggerTime;

        if triggerIndex <= numberOfDummyTriggers
            fprintf( ...
                '[Scanner] Received scanner trigger %d/%d\n', ...
                triggerIndex, numberOfDummyTriggers);
        else
            fprintf('[Scanner] Start trigger received.\n');
        end
    end

    scannerSync.first_trigger_abs = ...
        scannerSync.trigger_times_abs(1);

    scannerSync.experiment_start_abs = ...
        scannerSync.trigger_times_abs(end);

    scannerSync.trigger_times_rel = ...
        scannerSync.trigger_times_abs - ...
        scannerSync.first_trigger_abs;

    scannerSync.experiment_start_rel = ...
        scannerSync.experiment_start_abs - ...
        scannerSync.first_trigger_abs;

end


function [resp, rt, tOn] = rule_start_screen(w, rect, phase, trialData, textureCache, validKeys, escapeKey)
    utilities.screen.draw_trial_screen(w, rect, phase, trialData, textureCache, "");
    tOn = Screen('Flip', w);

    [~, responseTime] = utilities.screen.wait_key(validKeys, escapeKey);

    resp = "ready";
    rt = responseTime - tOn;
end


function [resp, rt, tOn, allResponses, allRts] = decision_screen( ...
    w, rect, phase, trialData, textureCache, ...
    sameKey, differentKey, escapeKey, duration)

    utilities.screen.draw_trial_screen(w, rect, phase, trialData, textureCache, "");
    tOn = Screen('Flip', w);

    [resp, rt, allResponses, allRts] = utilities.screen.collect_responses( ...
        w, rect, phase, trialData, textureCache, ...
        tOn, duration, sameKey, differentKey, escapeKey);
end


function [firstResponse, firstRt, allResponses, allRts] = collect_responses( ...
    w, rect, phase, trialData, textureCache, ...
    tOn, duration, sameKey, differentKey, escapeKey)

    firstResponse = "timeout";
    firstRt = NaN;

    allResponses = strings(0,1);
    allRts = [];

    deadline = tOn + duration;
    previousDown = false;

    while GetSecs() < deadline

        [isDown, keyTime, keyCode] = KbCheck;

        if isDown && ~previousDown

            if keyCode(escapeKey)
                error('Experiment aborted with ESC.');
            end

            if keyCode(sameKey) || keyCode(differentKey)

                currentResponse = "same";

                if keyCode(differentKey)
                    currentResponse = "different";
                end

                currentRt = keyTime - tOn;

                allResponses(end+1,1) = currentResponse; %#ok<AGROW>
                allRts(end+1,1) = currentRt; %#ok<AGROW>

                if firstResponse == "timeout"

                    firstResponse = currentResponse;
                    firstRt = currentRt;

                    utilities.screen.draw_trial_screen( ...
                        w, rect, phase, trialData, textureCache, currentResponse);

                    Screen('Flip', w);
                end
            end
        end

        previousDown = isDown;
        WaitSecs(0.001);
    end
end


function draw_trial_screen(w, rect, phase, trialData, textureCache, selectedResponse)
    utilities.screen.clear_screen(w);

    Screen('FrameRect', w, utilities.screen.phase_bg_rgb(phase.bg), rect, 30);

    utilities.screen.draw_header(w, rect, phase, selectedResponse);
    utilities.screen.draw_two_stacked_imgs(w, rect, textureCache, trialData.imgs);
end


function draw_header(w, rect, phase, selectedResponse)
    [hint, tip] = utilities.screen.phase_text(phase);

    Screen('TextStyle', w, 1);
    Screen('TextSize', w, 38);
    DrawFormattedText(w, char(hint), 'center', rect(4) * 0.12, [1 1 1]);

    Screen('TextStyle', w, 0);
    Screen('TextSize', w, 30);

    if string(phase.phase) == "inference" || string(phase.phase) == "application"
        utilities.screen.draw_decision_tip(w, rect, selectedResponse);
    else
        DrawFormattedText(w, char(tip), 'center', rect(4) * 0.18, [1 1 1]);
    end
end


function draw_decision_tip(w, rect, selectedResponse)
    y = rect(4) * 0.18;

    leftColor = [1 1 1];
    rightColor = [1 1 1];
    leftText = '←   Same';
    rightText = 'Different   →';

    if selectedResponse == "same"
        leftColor = [1 1 0];
    elseif selectedResponse == "different"
        rightColor = [1 1 0];
    end

    DrawFormattedText(w, leftText, rect(3) * 0.35, y, leftColor);
    DrawFormattedText(w, rightText, rect(3) * 0.57, y, rightColor);
end

function [hint, tip] = phase_text(phase)
    phaseName = string(phase.phase);

    if phaseName == "phase_start"
        parentPhase = string(phase.parent_phase);

        if parentPhase == "inference"
            hint = "First rule";
            tip = "←   Ready          Ready   →";
        elseif parentPhase == "application"
            hint = "Memorize this rule";
            tip = "←   Memorized      Memorized   →";
        else
            hint = "";
            tip = "";
        end

    elseif phaseName == "inference"
        hint = "Previous rule";
        tip = "←   Same          Different   →";

    elseif phaseName == "application"
        hint = "Memorized rule";
        tip = "←   Same          Different   →";

    else
        hint = "";
        tip = "";
    end
end


function draw_two_stacked_imgs(w, rect, textureCache, imgsField)
    imgs = utilities.session.to_cellstr(imgsField);

    topTexture = textureCache(char(imgs{1}));
    bottomTexture = textureCache(char(imgs{2}));

    gap = rect(4) * 0.06;
    imageWidth = rect(3) * 0.80;
    imageHeight = rect(4) * 0.30;

    topLimit = rect(4) * 0.22;
    bottomLimit = rect(4) * 0.94;

    stackHeight = 2 * imageHeight + gap;

    if stackHeight > bottomLimit - topLimit
        scale = (bottomLimit - topLimit) / stackHeight;
        imageWidth = imageWidth * scale;
        imageHeight = imageHeight * scale;
    end

    centerX = rect(3) / 2;
    centerY = (topLimit + bottomLimit) / 2;

    topRect = CenterRectOnPointd( ...
        [0 0 imageWidth imageHeight], ...
        centerX, centerY - imageHeight / 2 - gap / 2);

    bottomRect = CenterRectOnPointd( ...
        [0 0 imageWidth imageHeight], ...
        centerX, centerY + imageHeight / 2 + gap / 2);

    Screen('DrawTexture', w, topTexture, [], topRect);
    Screen('DrawTexture', w, bottomTexture, [], bottomRect);
end


function clear_screen(w)
    Screen('FillRect', w, [0.15 0.15 0.15]);
end


function text = optional_string(structData, fieldName)
    text = "";

    if isfield(structData, fieldName) && ~isempty(structData.(fieldName))
        text = string(structData.(fieldName));
    end
end


function rgb = phase_bg_rgb(bgName)
    luminosity = 0.4;

    switch string(bgName)
        case "yellow"
            baseRgb = [1 1 0];
        case "cyan"
            baseRgb = [0 1 1];
        otherwise
            rgb = [0 0 0];
            return
    end

    hsv = rgb2hsv(baseRgb);
    hsv(3) = luminosity;
    rgb = hsv2rgb(hsv);
end

end
end