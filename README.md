# ErgenOS Hyprland

A customized Hyprland session for ErgenOS, maintained by the ErgenOS project.
Independent project, not affiliated with or endorsed by the Hyprland project.

Optional preview: a separate tiled Wayland session alongside GNOME, using the
ErgenOS navy-and-blue styling. The session was validated on Hyprland 0.56.x;
newer Hyprland releases are accepted by the package so rolling-system updates
are not blocked, but still require normal runtime acceptance testing.
This repository contains session configuration and integration tools, not a fork
of the Hyprland compositor.

## Included components

- Coordinated panel, application launcher, lock screen and notification styling.
- Display, autostart, power, audio, brightness and desktop controls.
- Clipboard history, screenshots, session supervision and ordered logout.
- A separately packaged Waybar 0.15.0 build with exact tray-ID filtering.

## Build and install on ErgenOS / Arch Linux

Install build requirements (`base-devel`) and the dependencies listed in each
PKGBUILD. Run makepkg as an ordinary user. Install the panel helper first:

```sh
cd packages/ergenos-waybar
makepkg -si
cd ../ergenos-hyprland
makepkg -si
```

Log out and select **ErgenOS Hyprland** in the login screen. GNOME remains
available. The package does not seed or overwrite home configuration files.

## Documentation

- [Session installation, controls and behavior](packages/ergenos-hyprland/README.md)
- [Panel helper and patch](packages/ergenos-waybar/README.md)
- [Preview acceptance checklist](packages/ergenos-hyprland/RELEASE-CHECKLIST.md)
- [Recorded validation](packages/ergenos-hyprland/AUDIT.md)
- [Third-party inventory and open license checks](THIRD_PARTY.md)
- [License notices](LICENSES/README.md)

The preview has incomplete hardware and screen-sharing acceptance coverage.
Consult the checklist before treating it as a stable desktop release.

## Licensing

Original ErgenOS session code and configuration are GPL-3.0-or-later; see
[LICENSE](LICENSE). The Waybar patch is MIT, and upstream components retain
their own licenses. Artwork provenance gaps are recorded in THIRD_PARTY.md.
