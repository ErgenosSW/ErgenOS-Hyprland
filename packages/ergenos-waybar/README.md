# Private panel binary

Waybar 0.15.0 with a small exact-ID `tray.ignore-list` patch. The binary lives at
`/usr/lib/ergenos-hyprland/waybar`; the stock Waybar package, executable, agents,
D-Bus services and other desktops are retained. It is not a replacement provider.

Build and install this package before `../ergenos-hyprland` using `makepkg -si`.
The version bound intentionally requires review/rebuild when stock Waybar moves
past 0.15.0. This patch can be dropped when a suitable upstream filter is available
in a tested release. Keep source archives available when distributing binaries.

The filter matches exact SNI Id values, not positions or translated labels. It
keeps ignored items hidden on Status updates. Other tray items retain their
menus and activation. An empty filtered tray does not reserve icon space.
