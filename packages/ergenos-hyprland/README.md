# ErgenOS Hyprland - optional preview

A separate tiled Wayland session alongside GNOME, with the ErgenOS Continuous
navy panel, blue accents, original SVG icons, launcher and matching lock screen.
Preview status: not part of the default ISO. Tested with Hyprland 0.56.2.
See [AUDIT.md](AUDIT.md) for evidence and [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md)
for remaining acceptance checks.

## Installation

First build and install the adjacent `../ergenos-waybar` package with
`makepkg -si`, then build this profile as a normal user from this directory:

```sh
sudo pacman -Syu --needed base-devel
makepkg -si
```

Apart from the adjacent `ergenos-waybar` helper, dependencies come from official
Arch repositories. Do not run makepkg as
root. Hyprland must be 0.56.x; newer versions need an API compatibility review.
The build renders wallpaper.svg with librsvg and validates the native compositor,
terminal, launcher and notification configurations, desktop entry and regression
tests. Dependency versions and the complete source list live in PKGBUILD.

Save your work, log out, choose **ErgenOS Hyprland** in the login screen's session
picker and log in. Choose GNOME on a later login to return. For a TTY login use
`ergenos-hyprland-session`. Keep one graphical session per user because D-Bus
activation, portals, audio and keyring share that user's service manager.

Installation does not overwrite home configurations, change GDM or enable a
second default desktop. Polish keyboard layout is the default. Session tools and
notification-center controls are English; application content follows its locale.

## Everyday controls

| Action | Shortcut |
| --- | --- |
| Applications | Super, or Super+R |
| Terminal / Files | Super+Return / Super+E |
| Close / fullscreen / toggle floating | Super+Q / Super+F / Super+V |
| Focus / move a window | Super+arrows / Super+Shift+arrows |
| Workspaces / move window to workspace | Super+1-9 / Super+Shift+1-9 |
| Settings / shortcut reference | Super+comma / Super+F1 |
| Lock / session menu | Super+L / Super+Shift+E |
| Notification history / Do Not Disturb | Super+N / Super+Shift+N |
| Clipboard history | Super+Shift+V |
| Screenshot region / full screen to clipboard | Print / Shift+Print |

The logo opens applications; right-click opens Settings. Main panel icons open
network, Bluetooth, audio, brightness, battery and session controls. Right-click
audio to mute. Scroll audio/brightness to adjust. The three-dot drawer reveals
system tray icons. NetworkManager and Blueman tray icons are filtered by exact
ID because the panel already has network/Bluetooth controls. Their agents remain
running for network secrets and Bluetooth pairing. Filtering uses a private
Waybar 0.15.0 binary; the stock `/usr/bin/waybar` is retained. The bell opens notifications; right-click toggles Do Not
Disturb. A dot marks stored notifications and a crossed bell marks Do Not Disturb.

Use **Log out** from the session menu. Its helper stops background services and
waits before closing Wayland, avoiding hypridle 0.1.8's disconnect crash during
normal logout. Restart and Power off use the same ordering, after confirmation.
From a terminal use `ergenos-hyprland-exit logout`. A raw compositor exit or crash
bypasses that preparation.

## Settings and stored data

Open Settings with Super+comma or by right-clicking the logo:

- **Displays** uses nwg-displays. Apply and confirm before its rollback timer
  expires. The first use saves the current layout for rollback. Lua rules are
  saved in `~/.config/ergenos-hyprland/displays/`. Invalid files are kept as
  `.rejected-*.lua` while the last working rules are restored.
- **Autostart** respects XDG desktop restrictions and user-over-system precedence.
  Toggle entries or add an installed desktop launcher. Changes apply next login;
  disabling an entry does not kill it. New entries are scoped to Hyprland.
- **Power**, also available from battery details, shares standard power profiles
  with GNOME through power-profiles-daemon. Idle and lid preferences are separate
  session settings in `~/.config/ergenos-hyprland/power.json`. Defaults: lock after
  5 minutes, screen off after 10, no automatic suspend, system lid policy.
  Custom lid actions can keep the system running with an external display.
- **Clipboard history / Clear clipboard history** uses cliphist with text/image
  support, 100 items of up to 2 MiB each. Clear requires confirmation and also
  empties the current clipboard. The private runtime DB is mode 0600 and is
  removed at session-service shutdown. Recognized sensitive selections are
  skipped; detection depends on the sending app. Selected entries are copied,
  then pasted normally. Screenshots go to the clipboard without saving a file.

Notification history is held for the running SwayNotificationCenter process,
without a disk archive. It includes Clear all and Do Not Disturb; urgency handling
follows SwayNC. Notification contents use the sending application's language.

The session supervisor owns wallpaper, notification server, Polkit agent, power
manager, clipboard watchers and Waybar. The power manager owns one hypridle.
NetworkManager/Blueman follow XDG autostart. The custom session target is started
and stopped by the supervisor, without global enablement. Upstream portal
preferences select Hyprland for capture and GTK for fallback interfaces.
Hyprland-specific MIME defaults use Files/Nautilus for folders, VLC for audio
and video, Loupe for pictures, Papers for PDF/comic documents, and GNOME Text
Editor for plain text. Explicit user choices take priority; existing browser
defaults are retained.

Additional VLC decoding and subtitle plugins are optional dependencies. They are
not installed by this profile or its scripts. Users may explicitly install
`vlc-plugin-ffmpeg`, `vlc-plugin-freetype` and `vlc-plugin-ass` for additional
formats/subtitles. Supported formats depend on installed plugins; VLC and other
applications already bring some codec libraries through their normal dependencies.
This is not a claim that the ISO or the dependency tree is codec-free. Distribution
of a codec implementation may require a separate license/patent review for its
build and target countries; a user checkbox does not itself grant patent rights.

## Customization and upgrades

Create `~/.config/ergenos-hyprland/local.lua` for overrides, for example:

```lua
hl.config({ input = { kb_layout = "us" }, decoration = { rounding = 12 } })
```

Saved display rules load before local.lua, which can override them. Existing
`~/.config/hypr/` configurations are retained. Automatic compositor reload is
disabled because package replacement briefly removes files. After an upgrade run
`hyprctl reload`, or log out and log back in to restart updated services.
Rename a broken local.lua from GNOME or a TTY to recover.

Panel, launcher and lock-screen defaults are package-managed; edit their sources
and rebuild for deeper changes. No global GNOME or GTK appearance is imposed.
ErgenCTL, ErgenPac and Welcome are optional applications. XWayland is rendered
without compositor enlargement to avoid blurred Wine/game windows at fractional
scaling. X11 applications may need their own DPI/font settings. Native Wayland
applications retain normal display scaling. Battle.net with its Faugus Wine class
and exact title opens floating, centered, with room for its desktop layout. Both
the current `steam_app_wow` class and older `steam_app_default` entries are
supported. World of Warcraft with the same class and exact title starts floating
and fullscreen without geometry animations. Hyprland owns fullscreen while WoW
receives a native-sized window, preventing repeated XWayland fullscreen requests
from exposing Waybar without making a dual-monitor client select another output's
lower fullscreen resolution. A fresh launch was visually checked after the
original rule fixed the overlapping character-selection UI.
This package does not rewrite third-party launchers or change Wine prefix DPI.

## Removal

```sh
sudo pacman -R ergenos-hyprland
```

Review dependencies separately. User overrides remain in the home directory.

## Compatibility references

- [Hyprland 0.56.2 example](https://github.com/hyprwm/Hyprland/blob/v0.56.2/example/hyprland.lua)
- [Hypridle](https://wiki.hypr.land/hypr-ecosystem/user/hypridle/)
- [nwg-displays](https://github.com/nwg-piotr/nwg-displays)
- [SwayNotificationCenter](https://github.com/ErikReider/SwayNotificationCenter)
- [cliphist](https://github.com/sentriz/cliphist)

Original ErgenOS code/configuration use the repository's GPL-3.0-or-later license.
See THIRD_PARTY.md for asset provenance verification items.
Components retain their upstream licenses.

## Small tiled windows

Super+Shift+F toggles maximization while keeping the panel visible. Known apps
receive one automatic size correction per window lifetime after 1.5 seconds of
stable undersized geometry. Discord uses 940x500 logical pixels; responsive
ErgenCTL and ErgenPac use 360x300. If a tile is too small, it becomes a centered
floating window. Existing floating, fullscreen, hidden and grouped windows are
left alone. Super+V on the selected window restores tiling; that window will not
be corrected again until it is reopened. Unknown applications remain tiled.

Optional ~/.config/ergenos-hyprland/window-safety.json can override profiles:

```json
{"enabled": true, "profiles": {"discord": false, "example.app": [800, 500]}}
```

Changes are read automatically. Set enabled to false to disable the service.
Invalid settings retain the last valid policy. Small displays may still require
application zoom: maximization cannot make an interface responsive. This is a
compatibility fallback, not universal detection of application minimum sizes.

Late D-Bus notification activation is skipped when the ErgenOS Hyprland session
target is inactive. Other desktops retain upstream SwayNC activation behavior.
