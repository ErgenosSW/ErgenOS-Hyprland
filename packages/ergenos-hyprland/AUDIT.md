# Runtime validation - 2026-10-17

Status: optional preview. Tested system: Acer Nitro ANV16S61, AMD integrated GPU
and NVIDIA RTX 5050 Mobile, internal 1920x1200 display at 180 Hz / scale 1.5.
Hyprland 0.56.2. Audit candidate: package 0.1.0-25.

## Confirmed

- Native compositor/Foot/Fuzzel/desktop-entry/notification-schema validation and
  25 automated regressions pass. Tests cover session cleanup, singleton startup,
  screenshots/clipboard cancellation, exact text/image data, sensitive exclusion,
  monitor reload/rollback, XDG precedence, power settings and ordered logout.
- Panel, launcher, terminal, status controls, power UI, notification history and
  settings windows were inspected in the actual session. English session UI.
- User confirmed lock/unlock, suspend/resume and lid-close suspend returning to
  the lock screen. The actual session has valid audio/backlight endpoints.
- XDG autostart starts agents once. Real tests confirmed display-setting rollback
  without automatic config reload; external displays were not connected.
- Native portal FileChooser opens and closes; OpenURI opens the existing Brave
  default. Capture interfaces are advertised and ScreenCast CreateSession works.
- Live clipboard tests preserve text and images, skip recognized sensitive data
  and restore the preceding clipboard after tests. Full-screen PNG is 1920x1200.
- A real reboot, Hyprland -> GNOME -> Hyprland round trip and another real logout
  were tested. No leftover Hyprland processes/runtime DB in GNOME. Portal and
  notification owners follow the current desktop; no failed user units on return.
- Ordered menu logout in 0.1.0-19 prevented the earlier hypridle disconnect dump.
  Last tested clean exit: 22:40:49 Europe/Warsaw. The previous dump at 22:30:58
  predates this fix. Raw compositor exit/crash bypasses the menu ordering.

- Fresh ordinary account (UID 1001, no copied main-account settings) logged into
  Hyprland at 22:55:31 and exited cleanly at 22:55:45. User confirmed panel,
  launcher, terminal, settings, clipboard and lock. Account/home/private group
  removed after testing. Screenshot/notification workflows were not separately
  confirmed on this account; earlier main-account tests passed.

## Follow-up audit - 2026-10-17

- Current boot: no compositor config errors, no failed user units, one supervisor,
  one Waybar/SwayNC/hypridle, two clipboard watchers, one network/Bluetooth applet.
  All three portal services and the custom session target were active. Installed
  0.1.0-23 had 68 files with no integrity changes before this audit.
- Fixed the supervisor lock-file unlink race: only the outer session wrapper
  removes the lock after shutdown. A concurrent runner cannot acquire a new inode
  while cleanup still holds the previous lock.
- Display bridge restores saved files if a file disappears or config verification/
  reload fails. Regression cases exercise deletion, invalid files and failed reload.
- User local.lua now loads after all packaged window rules, matching documented
  override priority. Exit helper reports missing session context without traceback.
- Default application bindings were checked for actual desktop-entry support;
  audio/video use VLC, images Loupe, PDFs Papers, text Text Editor. User browser
  and explicit MIME choices remain higher priority.
- Native XWayland resolution and the scoped Battle.net/WoW rules were added after
  the initial audit. User and screenshot confirmed a fresh WoW launch with intact
  UI and its log detected 1920x1200 at 180 Hz (2026-10-16 23:39).
- Additional VLC plugins were installed only on the development machine and the
  user explicitly asked to keep them. They are optional dependencies of this
  profile, never automatically installed by it. No codec-free ISO claim is made.
- Package README, release checklist and review handoff now identify this candidate
  and distinguish fresh-profile MIME queries from actual graphical account tests.

## Tray duplication follow-up

The stock Waybar 0.15.0 lacks per-item filtering. `ergenos-waybar` installs a
private copy of the same release with a small exact SNI ID filter, without
replacing the system executable. The profile hides `nm-applet` and `blueman`;
network-secret and Bluetooth pairing agents keep running. A live separate tray
probe showed only the unrelated ChatGPT icon, with both ignored IDs recorded in
the log. No radio, connection or agent settings were changed.

## Pending acceptance

- Actual PipeWire screen-sharing stream in a browser. The picker appeared, then
  the user deferred this test; no capture frames were verified.
- External monitor hotplug, layout/scaling, docked lid policy and HDMI/DP audio:
  deferred until the user returns to Warsaw.
- Other machines/GPU combinations, webcam and Bluetooth pairing/audio are not
  covered by the current acceptance evidence.

## Observed upstream/system warnings

ACPI/UCSI firmware errors predate this profile. XWayland reports nonfatal keymap
limits. Existing Mako and SwayNC service descriptors advertise the same D-Bus
notification name, but only SwayNC runs in this session. Fuzzel downsizes a large
third-party icon. These observations do not establish a broken runtime feature.
A WirePlumber ACP warning was seen while speakers/microphones remained available;
external-display audio still requires a connected-monitor test.

The development account used earlier has application-specific Wayland flags and
other preferences. They are not installed by this package. Fresh-account testing
must therefore verify the packaged defaults independently.
