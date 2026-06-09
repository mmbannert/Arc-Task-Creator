classdef screen
methods(Static)

function [w, rect] = setup_window(config)
    Screen('Preference', 'SkipSyncTests', config.SKIP_SYNC_TESTS);
    Screen('Preference', 'Verbosity', 1);
    AssertOpenGL;

    PsychImaging('PrepareConfiguration');
    screenId = max(Screen('Screens'));
    
    if config.use_windowed_mode
        [w, rect] = PsychImaging('OpenWindow', screenId, config.bg_color, config.window_rect);
    else
        srcRect = [0, 0, 1400, 1400];
        dstRect = [420, 420, 1500, 1500]; % left bottom right top ?! whyyy :(
        PsychImaging('AddTask', 'General', 'UsePanelFitter', config.resolution, 'Custom', srcRect, dstRect);
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


function message_screen(w, ~, text)
    utilities.screen.clear_screen(w);
    Screen('TextStyle', w, 0);
    Screen('TextSize', w, 34);
    DrawFormattedText(w, char(string(text)), 'center', 'center', [1 1 1]);
    Screen('Flip', w);
end


function clear_screen(w)
    Screen('FillRect', w, [0.15 0.15 0.15]); % for light grayish background
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


function [resp, rt, tOn, allResponses, allRts] = trial_screen( ...
    w, rect, phase, trialData, textureCache, ...
    sameKey, differentKey, escapeKey, duration)

    utilities.screen.draw_trial(w, rect, phase, trialData, textureCache, "");
    tOn = Screen('Flip', w);

    [resp, rt, allResponses, allRts] = utilities.screen.collect_responses( ...
        w, rect, phase, trialData, textureCache, ...
        tOn, duration, sameKey, differentKey, escapeKey);
end


function [firstResponse, firstRt, allResponses, allRts] = collect_responses( ...
    w, rect, phase, trialData, textureCache, ...
    tOn, duration, sameKey, differentKey, escapeKey)
 
    firstResponse        = "timeout";
    firstRt              = NaN;
    allResponses         = strings(0, 1);
    allRts               = [];
    deadline             = tOn + duration;
    previousResponseDown = false;
 
    while GetSecs() < deadline
        [isDown, keyTime, keyCode] = KbCheck;
 
        if ~isDown
            previousResponseDown = false;
            WaitSecs(0.001);
            continue
        end
 
        if keyCode(escapeKey), error('Experiment aborted with ESC.'); end
 
        isNewPress           = (keyCode(sameKey) || keyCode(differentKey)) && ~previousResponseDown;
        previousResponseDown = keyCode(sameKey) || keyCode(differentKey);
 
        if ~isNewPress, continue; end
 
        responseOptions = ["same", "different"];
        response        = responseOptions(1 + keyCode(differentKey));
        rt                  = keyTime - tOn;
        allResponses(end+1) = response; %#ok<AGROW>
        allRts(end+1)       = rt;       %#ok<AGROW>
 
        if firstResponse == "timeout"
            firstResponse = response;
            firstRt       = rt;
            utilities.screen.draw_trial(w, rect, phase, trialData, textureCache, response);
            Screen('Flip', w);
        end
    end
end

function draw_trial(w, rect, phase, trialData, textureCache, selectedResponse)
    utilities.screen.clear_screen(w);
    Screen('FrameRect', w, utilities.screen.phase_bg_rgb(phase.bg), rect, 30);
    utilities.screen.draw_header(w, rect, phase, selectedResponse);
    utilities.screen.draw_two_stacked_imgs(w, rect, textureCache, trialData.imgs);
end



function draw_header(w, rect, phase, selectedResponse)
    [hint, leftText, rightText] = utilities.screen.phase_text(phase);

    Screen('TextStyle', w, 1);
    Screen('TextSize', w, 38);
    DrawFormattedText(w, char(hint), 'center', rect(4) * 0.12, [1 1 1]);

    Screen('TextStyle', w, 0);
    Screen('TextSize', w, 30);

    utilities.screen.draw_response_tip(w, rect, selectedResponse, leftText, rightText);
end



function draw_response_tip(w, rect, selectedResponse, leftText, rightText)
    y = rect(4) * 0.18;

    leftColor = [1 1 1];
    rightColor = [1 1 1];

    if selectedResponse == "same"
        leftColor = [1 1 0];
    elseif selectedResponse == "different"
        rightColor = [1 1 0];
    end

    centerX = rect(3) / 2;
    gap = rect(3) * 0.08;

    DrawFormattedText(w, char(leftText), 'right', y, leftColor, [], [], [], [], [], [0 0 centerX - gap rect(4)]);
    DrawFormattedText(w, char(rightText), centerX + gap, y, rightColor);
end

function [hint, leftText, rightText] = phase_text(phase)
    phaseName = string(phase.phase);

    switch phaseName
        case "inference_start"
            hint = "First rule";
            leftText = "←   Ready";
            rightText = "Ready   →";

        case "application_start"
            hint = "Memorize this rule";
            leftText = "←   Memorized";
            rightText = "Memorized   →";

        case "inference"
            hint = "Previous rule";
            leftText = "←   Same";
            rightText = "Different   →";

        case "application"
            hint = "Memorized rule";
            leftText = "←   Same";
            rightText = "Different   →";
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

    scale       = min(1, (bottomLimit - topLimit) / (2 * imageHeight + gap));
    imageWidth  = imageWidth  * scale;
    imageHeight = imageHeight * scale;

    centerX = rect(3) / 2;
    centerY = (topLimit + bottomLimit) / 2;

    topRect = CenterRectOnPointd([0 0 imageWidth imageHeight], ...
        centerX, centerY - imageHeight / 2 - gap / 2);

    bottomRect = CenterRectOnPointd([0 0 imageWidth imageHeight], ...
        centerX, centerY + imageHeight / 2 + gap / 2);

    Screen('DrawTexture', w, topTexture, [], topRect);
    Screen('DrawTexture', w, bottomTexture, [], bottomRect);
end



function rgb = phase_bg_rgb(bgName)
    luminosity = 0.4;

    switch string(bgName)
        case "yellow",        baseRgb = [1 1 0];
        case "cyan",          baseRgb = [0 1 1];
        otherwise,            rgb = [0 0 0];
            return
    end

    hsv = rgb2hsv(baseRgb);
    hsv(3) = luminosity;
    rgb = hsv2rgb(hsv);
end

end
end