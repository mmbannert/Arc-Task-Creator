classdef screen_utils
methods(Static)

function [w, rect] = setup_window(cfg)
    Screen('Preference', 'SkipSyncTests', cfg.SKIP_SYNC_TESTS);
    AssertOpenGL;

    PsychImaging('PrepareConfiguration');

    screen_id = max(Screen('Screens'));

    PsychImaging('AddTask', 'General', 'UsePanelFitter', cfg.resolution, 'Aspect');

    if cfg.use_windowed_mode
        [w, rect] = PsychImaging('OpenWindow', screen_id, cfg.bg_color, cfg.window_rect);
    else
        [w, rect] = PsychImaging('OpenWindow', screen_id, cfg.bg_color);
    end

    Screen('ColorRange', w, 1);
    Screen('TextFont', w, 'Arial');

    fprintf('PTB window opened on screen %d.\n', screen_id);
end


function [key, t] = wait_key(validKeys, escKey)
    KbReleaseWait;

    while true
        [down, secs, kc] = KbCheck;

        if ~down
            continue
        end

        if kc(escKey)
            error('Experiment aborted with ESC.');
        end

        if any(kc(validKeys))
            key = find(kc, 1, 'first');
            t = secs;
            KbReleaseWait;
            return
        end
    end
end


function message_screen(w, rect, text)

    % ---- gray background ----
    bgColor = [0.15 0.15 0.15];
    Screen('FillRect', w, bgColor);

    % ---- text ----
    Screen('TextStyle', w, 0);
    Screen('TextSize', w, 34);

    DrawFormattedText( ...
        w, ...
        char(string(text)), ...
        'center', ...
        'center', ...
        [1 1 1]);

    Screen('Flip', w);

end


function fixation_screen(w, rect, seconds)

    % ---- gray background ----
    bgColor = [0.15 0.15 0.15];
    Screen('FillRect', w, bgColor);

    % ---- fixation cross ----
    crossColor = [1 1 1];

    crossSize = 20;
    lineWidth = 4;

    xCenter = rect(3) / 2;
    yCenter = rect(4) / 2;

    % Horizontal line
    Screen('DrawLine', ...
        w, crossColor, ...
        xCenter - crossSize, yCenter, ...
        xCenter + crossSize, yCenter, ...
        lineWidth);

    % Vertical line
    Screen('DrawLine', ...
        w, crossColor, ...
        xCenter, yCenter - crossSize, ...
        xCenter, yCenter + crossSize, ...
        lineWidth);

    % ---- flip ----
    tOn = Screen('Flip', w);

    % ---- precise timing ----
    WaitSecs('UntilTime', tOn + seconds);

end

function [resp, rt, tOn] = rule_start_screen(w, rect, phase, tr, texCache, validKeys, keyEsc)
    utilities.screen_utils.draw_trial_screen(w, rect, phase, tr, texCache);

    tOn = Screen('Flip', w);

    [~, respTime] = utilities.screen_utils.wait_key(validKeys, keyEsc);

    rt = respTime - tOn;
    resp = "ready";
end


function [resp, rt, tOn] = twoimg_screen(w, rect, phase, tr, texCache, keySame, keyDiff, keyEsc)
    utilities.screen_utils.draw_trial_screen(w, rect, phase, tr, texCache);

    tOn = Screen('Flip', w);

    [respKey, respTime] = utilities.screen_utils.wait_key([keySame keyDiff], keyEsc);

    rt = respTime - tOn;

    if respKey == keyDiff
        resp = "different";
    else
        resp = "same";
    end
end


function draw_trial_screen(w, rect, phase, tr, texCache)
    Screen('FillRect', w, [0.15 0.15 0.15]);

    frameColor = utilities.screen_utils.phase_bg_rgb(phase.bg);
    frameWidth = 30;

    Screen('FrameRect', w, frameColor, rect, frameWidth);

    utilities.screen_utils.draw_header(w, rect, phase);

    if isfield(tr, 'imgs') && ~isempty(tr.imgs)
        utilities.screen_utils.draw_two_stacked_imgs(w, rect, texCache, tr.imgs);
    else
        DrawFormattedText(w, '[missing imgs field]', 'center', rect(4) * 0.6, [1 1 1]);
    end
end


function draw_header(w, rect, phase)
    hint = "";
    tip = "";

    if isfield(phase, 'hint') && ~isempty(phase.hint)
        hint = string(phase.hint);
    end

    if isfield(phase, 'tip') && ~isempty(phase.tip)
        tip = string(phase.tip);
    end

    Screen('TextStyle', w, 1);
    Screen('TextSize', w, 38);
    DrawFormattedText(w, char(hint), 'center', rect(4) * 0.12, [1 1 1]);

    Screen('TextStyle', w, 0);
    Screen('TextSize', w, 30);
    DrawFormattedText(w, char(tip), 'center', rect(4) * 0.18, [1 1 1]);
end


function draw_two_stacked_imgs(w, rect, texCache, imgsField)
    imgs = utilities.session_utils.to_cellstr(imgsField);

    if numel(imgs) < 2
        DrawFormattedText(w, '[need 2 imgs]', 'center', rect(4) * 0.6, [1 1 1]);
        return
    end

    keyTop = char(imgs{1});
    keyBot = char(imgs{2});

    GAP = rect(4) * 0.06;
    wImg = rect(3) * 0.80;
    hImg = rect(4) * 0.30;

    topMargin = rect(4) * 0.22;
    bottomMargin = rect(4) * 0.06;

    availTop = topMargin;
    availBot = rect(4) - bottomMargin;

    stackH = 2 * hImg + GAP;
    centerX = rect(3) / 2;
    centerY = (availTop + availBot) / 2;

    if stackH > (availBot - availTop)
        scale = (availBot - availTop) / stackH;
        hImg = hImg * scale;
        wImg = wImg * scale;
    end

    dstTop = CenterRectOnPointd( ...
        [0 0 wImg hImg], ...
        centerX, ...
        centerY - (hImg / 2 + GAP / 2));

    dstBot = CenterRectOnPointd( ...
        [0 0 wImg hImg], ...
        centerX, ...
        centerY + (hImg / 2 + GAP / 2));

    if isKey(texCache, keyTop)
        Screen('DrawTexture', w, texCache(keyTop), [], dstTop);
    else
        DrawFormattedText(w, '[missing top]', 'center', rect(4) * 0.55, [1 1 1]);
    end

    if isKey(texCache, keyBot)
        Screen('DrawTexture', w, texCache(keyBot), [], dstBot);
    else
        DrawFormattedText(w, '[missing bottom]', 'center', rect(4) * 0.80, [1 1 1]);
    end
end


function rgb = phase_bg_rgb(bgName)
    luminosity = 0.4;

    switch string(bgName)
        case "yellow"
            base_rgb = [1 1 0];
        case "cyan"
            base_rgb = [0 1 1];
        otherwise
            rgb = [0 0 0];
            return
    end

    hsv = rgb2hsv(base_rgb);
    hsv(3) = luminosity;
    rgb = hsv2rgb(hsv);
end

end
end