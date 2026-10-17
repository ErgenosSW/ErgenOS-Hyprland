# Third-party components and license inventory

Snapshot: 2026-10-17. Scope: the `ergenos-hyprland` session package and adjacent
`ergenos-waybar` package, not the complete ErgenOS ISO or all transitive libraries.

This is an inventory and release preparation record, not a completed license audit.
Versions and license expressions below were read from the local pacman database;
they describe this installed snapshot, not every supported version. Ambiguous legacy
labels are preserved rather than guessed. Upstream URLs are recorded per package.

## Project boundary

ErgenOS Hyprland is a session and integration layer using upstream Hyprland.
The package does not build a modified Hyprland compositor. Its own scripts,
configuration and artwork are currently declared GPL-3.0-or-later by PKGBUILD
and README. The repository root contains the GPLv3 license text in `LICENSE`.
For a standalone repository, carry that text plus an explicit GPL-3.0-or-later
grant for the original files whose rights are controlled by the project.
Do not apply that declaration to third-party code or assets by assumption.

## Modified upstream code: Waybar

`../ergenos-waybar/PKGBUILD` fetches the Waybar 0.15.0 release archive and applies
`tray-ignore-list.patch`. It builds `/usr/lib/ergenos-hyprland/waybar`, leaving
the system binary in place. The patch adds exact tray ID filtering, retains
item status and excludes filtered items when deciding tray visibility.

The package declares MIT and already installs the upstream license at
`/usr/share/licenses/ergenos-waybar/LICENSE`. Preserve the full upstream copyright,
permission and disclaimer text. The installed standard Waybar license snapshot
identifies Copyright (c) 2025 Alex; verify the release archive's own LICENSE when
preparing the release. Keep the source archive URL, checksum and patch available.
Review the selected build's bundled sources and dependency notices as well;
this component-level table does not inventory the binary's full dependency tree.
When moving the patch to another repository, document its own licensing explicitly.

## Runtime dependencies

| Package | Installed version | License metadata | Role | Upstream |
| --- | --- | --- | --- | --- |
| hyprland | 0.56.2-4 | BSD-3-Clause | Wayland compositor; unmodified package dependency | https://github.com/hyprwm/Hyprland |
| hyprland | 0.56.2-4 | BSD-3-Clause | Wayland compositor; unmodified package dependency | https://github.com/hyprwm/Hyprland |
| waybar | 0.15.0-3 | MIT | System panel package and runtime libraries | https://github.com/Alexays/Waybar/ |
| ergenos-waybar | 0.15.0-1 | MIT | Waybar 0.15.0 rebuilt with tray-ignore-list.patch; modified binary | https://github.com/Alexays/Waybar |
| fuzzel | 1.15.0-1 | MIT | Application and session menu launcher | https://codeberg.org/dnkl/fuzzel |
| swaync | 0.12.6-1 | GPL-3.0-only | Notifications and notification center; upstream CSS imported at runtime | https://github.com/ErikReider/SwayNotificationCenter |
| hyprlock | 0.9.6-3 | BSD-3-Clause | Lock screen | https://github.com/hyprwm/hyprlock |
| hypridle | 0.1.8-2 | BSD-3-Clause | Idle actions | https://github.com/hyprwm/hypridle |
| swaybg | 1.2.2-1 | MIT | Wallpaper renderer | https://github.com/swaywm/swaybg |
| foot | 1.28.0-2 | MIT | Terminal | https://codeberg.org/dnkl/foot |
| polkit-gnome | 0.105-12 | LGPL-2.0-or-later | System/service integration | https://gitlab.gnome.org/Archive/policykit-gnome |
| network-manager-applet | 1.36.0-2 | GPL-2.0-or-later | System/service integration | https://gitlab.gnome.org/GNOME/network-manager-applet |
| networkmanager | 1.58.1-2 | LGPL-2.1-or-later  GPL-2.0-or-later | System/service integration | https://networkmanager.dev/ |
| blueman | 2.4.6-2 | GPL-3.0-or-later | System/service integration | https://github.com/blueman-project/blueman |
| nwg-displays | 0.4.4-1 | MIT | Display configuration | https://github.com/nwg-piotr/nwg-displays |
| xdg-desktop-portal-hyprland | 1.4.1-2 | MIT | System/service integration | https://github.com/hyprwm/xdg-desktop-portal-hyprland |
| xdg-desktop-portal-gtk | 1.15.3-1 | LGPL-2.0-or-later | System/service integration | https://github.com/flatpak/xdg-desktop-portal-gtk |
| gnome-keyring | 1:51.1-1 | GPL-2.0-or-later  LGPL-2.1-or-later | System/service integration | https://gitlab.gnome.org/GNOME/gnome-keyring |
| pipewire | 1:1.6.9-1 | MIT  LGPL-2.1-or-later | System/service integration | https://pipewire.org |
| pipewire-pulse | 1:1.6.9-1 | MIT | System/service integration | https://pipewire.org |
| wireplumber | 0.5.18-1 | MIT | System/service integration | https://pipewire.pages.freedesktop.org/wireplumber/ |
| rtkit | 0.14-1 | GPL-3.0-or-later AND MIT | System/service integration | https://gitlab.freedesktop.org/pipewire/rtkit |
| pavucontrol | 1:6.2-1 | GPL-2.0-or-later | System/service integration | https://freedesktop.org/software/pulseaudio/pavucontrol/ |
| power-profiles-daemon | 0.30-1 | GPL-3.0-only | System/service integration | https://gitlab.freedesktop.org/upower/power-profiles-daemon |
| upower | 1.91.5-1 | GPL-2.0-or-later | System/service integration | https://upower.freedesktop.org |
| brightnessctl | 0.5.1-3 | MIT | System/service integration | https://github.com/Hummer12007/brightnessctl |
| playerctl | 2.4.1-5 | LGPL-3.0-only | System/service integration | https://github.com/altdesktop/playerctl |
| grim | 1.5.0-2 | MIT | Screenshot capture | https://gitlab.freedesktop.org/emersion/grim |
| slurp | 1.5.0-2 | MIT | Screenshot region selection | https://github.com/emersion/slurp |
| wl-clipboard | 1:2.3.0-1 | GPL-3.0-or-later | Clipboard access and watchers | https://github.com/bugaevc/wl-clipboard |
| cliphist | 1:0.7.0-2 | GPL3 | Clipboard history | https://github.com/sentriz/cliphist |
| xdg-utils | 1.2.1-2 | MIT | System/service integration | https://gitlab.freedesktop.org/xdg/xdg-utils |
| libnotify | 0.8.8-1 | LGPL-2.1-or-later | System/service integration | https://gitlab.gnome.org/GNOME/libnotify |
| nautilus | 51.1-1 | GPL-3.0-or-later | System/service integration | https://apps.gnome.org/Nautilus/ |
| vlc | 3.0.24-1 | GPL-2.0-or-later  LGPL-2.1-or-later | System/service integration | https://www.videolan.org/vlc/ |
| loupe | 51.0-1 | GPL-3.0-or-later | System/service integration | https://apps.gnome.org/Loupe/ |
| papers | 51.1-1 | GPL-2.0-or-later | System/service integration | https://apps.gnome.org/Papers/ |
| gnome-text-editor | 51.0-1 | GPL-3.0-or-later | System/service integration | https://apps.gnome.org/TextEditor/ |
| python | 3.14.8-1 | PSF-2.0 | System/service integration | https://www.python.org/ |
| python-gobject | 3.58.1-1 | LGPL-2.1-or-later | Python bindings for GTK, GLib and libadwaita | https://pygobject.gnome.org/ |
| gtk4 | 1:4.24.1-1 | LGPL-2.1-or-later | Settings UI toolkit | https://www.gtk.org/ |
| libadwaita | 1:1.10.0-1 | LGPL-2.1-or-later | Settings UI components | https://gnome.pages.gitlab.gnome.org/libadwaita/ |
| inter-font | 4.1-1 | OFL-1.1-RFN | UI font; font files supplied by dependency | https://github.com/rsms/inter |
| bash | 5.3.20-1 | GPL-3.0-or-later | System/service integration | https://www.gnu.org/software/bash/bash.html |
| util-linux | 2.42.4-1 | BSD-2-Clause  BSD-3-Clause  BSD-4-Clause-UC  GPL-2.0-only  GPL-2.0-or-later  GPL-3.0-or-later  ISC  LGPL-2.1-or-later  LicenseRef-PublicDomain | System/service integration | https://github.com/util-linux/util-linux |
| dbus | 1.16.2-1 | AFL-2.1 OR GPL-2.0-or-later | System/service integration | https://www.freedesktop.org/wiki/Software/dbus/ |
| systemd | 262-1 | LGPL-2.1-or-later  CC0-1.0  GPL-2.0-or-later  MIT-0 | System/service integration | https://www.github.com/systemd/systemd |
| procps-ng | 4.0.7-1 | GPL  LGPL | System/service integration | https://gitlab.com/procps-ng/procps |

## Build and validation dependencies

| Package | Installed version | License metadata | Role | Upstream |
| --- | --- | --- | --- | --- |
| librsvg | 2:2.63.2-1 | LGPL-2.1-or-later | Build-time SVG wallpaper rendering | https://gitlab.gnome.org/GNOME/librsvg |
| lua | 5.5.1-1 | MIT | Build-time Lua checks | https://www.lua.org/ |
| python | 3.14.8-1 | PSF-2.0 | Build/validation tool | https://www.python.org/ |
| desktop-file-utils | 0.28-1 | GPL-2.0-or-later | Build/validation tool | https://www.freedesktop.org/wiki/Software/desktop-file-utils |
| python-jsonschema | 4.26.0-1 | MIT | Build-time schema validation | https://github.com/python-jsonschema/jsonschema |

## Optional integrations

| Package | Installed version | License metadata | Role | Upstream |
| --- | --- | --- | --- | --- |
| vlc-plugin-ffmpeg | 3.0.24-1 | GPL-2.0-or-later  LGPL-2.1-or-later | Optional application/codec integration | https://www.videolan.org/vlc/ |
| vlc-plugin-freetype | 3.0.24-1 | GPL-2.0-or-later  LGPL-2.1-or-later | Optional application/codec integration | https://www.videolan.org/vlc/ |
| vlc-plugin-ass | 3.0.24-1 | GPL-2.0-or-later  LGPL-2.1-or-later | Optional application/codec integration | https://www.videolan.org/vlc/ |
| ergenctl | 1.1.0.dev-10 | GPL-3.0-or-later | Optional application/codec integration | https://github.com/ErgenosSW/ErgenCTL |
| ergenpac | 1.0.1-2 | GPL-3.0-or-later | Optional application/codec integration | https://github.com/ErgenosSW/ErgenPac |
| ergenos-welcome | 1.0.3-1 | GPL-3.0-or-later | Optional application/codec integration | https://github.com/ErgenosSW/ErgenOS-Welcome |

## Further system components used indirectly

The session also uses GLib/GIO command-line tools such as `gdbus`, the main
`xdg-desktop-portal` service, the Wayland graphics stack, XWayland for X11 clients,
Mesa/drivers, font and icon resolution and the libraries pulled in by its direct
dependencies. Record the resolved package closure and license data separately
for each binary/ISO release. A top-level dependency list is not a full SBOM.
GNOME/GDM login integration is part of the surrounding OS deployment.
Zsh, Powerlevel10k, shell plugins, Wine and Battle.net are not shipped by this
session package; inventory them separately if included in an ISO or release bundle.

## Artwork, fonts and reference material

- Session `panel-*.svg`, `battery-*.svg`, `wallpaper.svg` and `logo.png`
  require a provenance record. README describes
  original ErgenOS SVG icons, but that statement alone does not establish the
  origin and rights for every file. No per-asset attribution was found in the
  reviewed top-level SVG files. Confirm creation/source, author and grant before
  marking the complete asset set as original GPL artwork.
- The original working tree also contains concept artwork with embedded images.
  Those design-only files are not included in this repository; review their
  embedded content before adding them later.
- Inter is selected in the UI configuration. Its installed package declares
  OFL-1.1-RFN, and `/usr/share/licenses/inter-font/LICENSE.txt` contains the
  Inter Project Authors notice and SIL OFL 1.1 text. Preserve those terms if
  redistributing the font; do not relicense font files under GPL.
- Foot requests the system `monospace` alias. The actual font depends on the
  machine and is not identified by that alias. Launcher application icons also
  come from installed applications/icon themes; record any font/icon theme files
  actually bundled with a release.
- README cites the Hyprland v0.56.2 example configuration. Record any copied or
  adapted portions and preserve the corresponding BSD-3-Clause notices.
- `notifications.css` imports `/etc/xdg/swaync/style.css` at runtime. SwayNC is
  GPL-3.0-only. Its upstream stylesheet remains separately licensed; if copying
  or adapting it into the project, retain its applicable license and notices.

## Release documentation to prepare

1. `LICENSE`: GPLv3 text and a clear GPL-3.0-or-later grant for original project
   material; retain third-party exceptions and any per-file terms.
2. `THIRD_PARTY.md`: this inventory, with provenance gaps resolved and versions
   refreshed for the release.
3. `LICENSES/` or a notices directory: actual upstream license texts and copyright
   notices for copied, modified or bundled material, including Waybar when shipped.
   Copy notices from the exact sources used, not just generic license templates.
4. Source/release manifest: source URLs, revisions, patches, checksums and build
   instructions. If distributing GPL-covered binaries or an ISO, arrange the
   corresponding-source delivery required by the applicable licenses. A credits
   table alone does not fulfill those requirements.
5. Package integration: the session package installs this inventory as documentation.
   The repository root also carries the GPLv3 text and Waybar MIT notice.
   The Waybar helper installs its exact upstream license during packaging.

## Open verification items

- Resolve `cliphist` metadata `GPL3` against the exact v0.7.0 source license and
  file headers before choosing an SPDX `only` or `or-later` suffix.
- Resolve procps-ng's legacy `GPL LGPL` metadata at component/file level if
  redistributed. Multi-license package fields elsewhere describe package contents;
  they do not automatically mean every license is an alternative choice.
- Confirm asset provenance, including the logo; review concept images if added later.
- Audit bundled/transitive contents of each binary or ISO actually published.
- Preserve the distinction between upstream project credits, license notices,
  source-delivery requirements and ErgenOS branding permissions.

## Primary reference

Hyprland v0.56.2 BSD-3-Clause license:
https://github.com/hyprwm/Hyprland/blob/v0.56.2/LICENSE

Local evidence: both PKGBUILDs, README, session scripts, UI imports/configuration,
installed package metadata and installed Waybar/Inter license files. This inventory
has not verified the complete upstream source tree for every dependency.
