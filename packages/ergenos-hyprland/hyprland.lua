-- ErgenOS tiled session. User overrides are loaded last; GNOME is untouched.
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = "auto" })
hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
hl.config({
    general = {
        layout = "dwindle", gaps_in = 6, gaps_out = 14, border_size = 2,
        resize_on_border = true,
        col = {
            active_border = { colors = { "rgba(0aa7ffee)", "rgba(0068ffee)" }, angle = 45 },
            inactive_border = "rgba(8fbeeb29)",
        },
    },
    decoration = {
        rounding = 16,
        shadow = { enabled = true, range = 18, render_power = 3, color = 0x66000000 },
        blur = { enabled = true, size = 3, passes = 2 },
    },
    animations = { enabled = true },
    -- Render X11/Wine at native pixels; applications handle their own DPI.
    xwayland = { force_zero_scaling = true },
    dwindle = { preserve_split = true },
    input = { kb_layout = "pl", follow_mouse = 1, touchpad = { natural_scroll = true, tap_to_click = true } },
    misc = { disable_hyprland_logo = true, force_default_wallpaper = 0, disable_autoreload = true },
})
hl.curve("ergenEase", { type = "bezier", points = { { 0.2, 0.8 }, { 0.2, 1 } } })
hl.animation({ leaf = "windows", enabled = true, speed = 3, bezier = "ergenEase" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 3, bezier = "ergenEase", style = "slide" })
hl.animation({ leaf = "fade", enabled = true, speed = 3, bezier = "ergenEase" })
hl.on("hyprland.start", function() hl.exec_cmd("/usr/lib/ergenos-hyprland/session-services") end)
local function exec(key, command, options) hl.bind(key, hl.dsp.exec_cmd(command), options) end
exec("SUPER + Return", "foot --config=/usr/share/ergenos-hyprland/foot.ini")
exec("SUPER + E", "nautilus --new-window")
exec("SUPER + R", "ergenos-hyprland-menu")
-- Release-only binding; Super+R remains available as an explicit launcher shortcut.
exec("SUPER + Super_L", "ergenos-hyprland-menu", { release = true })
exec("SUPER + L", "loginctl lock-session")
exec("SUPER + SHIFT + E", "ergenos-hyprland-menu session")
exec("SUPER + F1", "ergenos-hyprland-menu help")
exec("Print", "ergenos-hyprland-screenshot")
exec("SHIFT + Print", "ergenos-hyprland-screenshot screen")
hl.bind("SUPER + Q", hl.dsp.window.close())
hl.bind("SUPER + V", hl.dsp.window.float({ action = "toggle" }))
hl.bind("SUPER + J", hl.dsp.layout("togglesplit"))
hl.bind("SUPER + SHIFT + left", hl.dsp.window.move({ direction = "left" }))
hl.bind("SUPER + SHIFT + right", hl.dsp.window.move({ direction = "right" }))
hl.bind("SUPER + SHIFT + up", hl.dsp.window.move({ direction = "up" }))
hl.bind("SUPER + SHIFT + down", hl.dsp.window.move({ direction = "down" }))
exec("SUPER + SHIFT + V", "ergenos-hyprland-clipboard")
exec("SUPER + N", "swaync-client --toggle-panel")
exec("SUPER + SHIFT + N", "swaync-client --toggle-dnd")
exec("SUPER + comma", "ergenos-hyprland-menu settings")
hl.bind("SUPER + F", hl.dsp.window.fullscreen({ action = "toggle", mode = "fullscreen" }))
hl.bind("SUPER + SHIFT + F", hl.dsp.window.fullscreen({ action = "toggle", mode = "maximized" }))
for _, direction in ipairs({ "left", "right", "up", "down" }) do
    hl.bind("SUPER + " .. direction, hl.dsp.focus({ direction = direction }))
end
for workspace = 1, 9 do
    hl.bind("SUPER + " .. workspace, hl.dsp.focus({ workspace = workspace }))
    hl.bind("SUPER + SHIFT + " .. workspace, hl.dsp.window.move({ workspace = workspace }))
end
hl.bind("SUPER + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind("SUPER + mouse:273", hl.dsp.window.resize(), { mouse = true })
exec("XF86AudioRaiseVolume", "wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+", { locked = true, repeating = true })
exec("XF86AudioLowerVolume", "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-", { locked = true, repeating = true })
exec("XF86AudioMute", "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle", { locked = true })
exec("XF86AudioMicMute", "wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle", { locked = true })
exec("XF86MonBrightnessUp", "brightnessctl set +5%", { locked = true, repeating = true })
exec("XF86MonBrightnessDown", "brightnessctl --min-value=1 set 5%-", { locked = true, repeating = true })
exec("XF86AudioPlay", "playerctl play-pause", { locked = true })
exec("XF86AudioNext", "playerctl next", { locked = true })
exec("XF86AudioPrev", "playerctl previous", { locked = true })
local config_home = os.getenv("XDG_CONFIG_HOME") or (os.getenv("HOME") .. "/.config")
-- Saved display rules are optional and precede explicit local overrides.
for _, name in ipairs({ "monitors.lua", "workspaces.lua" }) do
    local path = config_home .. "/ergenos-hyprland/displays/" .. name
    local saved = io.open(path, "r")
    if saved then
        saved:close()
        local ok, message = pcall(dofile, path)
        if not ok then error("Display configuration: " .. tostring(message)) end
    end
end

-- Keep compact panel controls above the tiled workspace.
hl.window_rule({ name = "ergenos-desktop-controls", match = { class = "io.github.ergenossw.HyprlandControls" }, float = true, center = true })
-- Settings windows need enough room independently of the current tile split.
hl.window_rule({ name = "ergenos-autostart-settings", match = { class = "io.github.ergenossw.HyprlandAutostart" }, float = true, center = true, size = "570 520" })
hl.window_rule({ name = "ergenos-display-settings", match = { class = "nwg-displays" }, maximize = true })

hl.window_rule({ name = "ergenos-power-settings", match = { class = "io.github.ergenossw.HyprlandPower" }, float = true, center = true, size = "540 650" })

-- Battle.net's fixed desktop layout must not be squeezed into a narrow tile.
-- Its Wine class is shared by other programs, so also require the exact title.
hl.window_rule({ name = "ergenos-battlenet", match = { class = "^steam_app_default$", title = "^Battle[.]net$" }, float = true, center = true, size = "1100 680" })

-- Wine can retain an inconsistent viewport while its initial window is resized.
-- Keep this specific game out of tiling and animated geometry transitions.
hl.window_rule({ name = "ergenos-wow", match = { class = "^steam_app_default$", title = "^World of Warcraft$" }, float = true, fullscreen = true, no_anim = true })

-- Local overrides follow all packaged defaults, including window rules.
local override = config_home .. "/ergenos-hyprland/local.lua"
local file = io.open(override, "r")
if file then file:close(); dofile(override) end
