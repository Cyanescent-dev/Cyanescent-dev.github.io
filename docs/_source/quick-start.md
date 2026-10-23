# Cyanescent Player 1.0.0 — Quick Start

Music-responsive visuals and video creation. Version 1.0.0, build 2.
Official website and support starting point: [cyanescent-dev.github.io](https://cyanescent-dev.github.io).

## Requirements and editions

macOS 12 or later; universal applications support Apple Silicon and Intel. A GPU/driver capable of WebGL 2 in macOS WebKit is required. Start with Standard quality and increase it if playback remains smooth. There is no certified minimum GPU/VRAM matrix; 4K export and complex worlds can require substantially more time and memory. Native System Audio capture requires macOS 14.2 or later. Pocket Scion requires compatible USB-MIDI hardware. Optional worlds need separate disk space.

| Edition | Included presets | Maximum export | Additional content |
|---|---:|---|---|
| Free (application named Cyanescent Player) | 18 curated real-time presets | 1080p | Rendered transitions |
| Pro | 75 real-time presets | 4K | Rendered transitions |
| Pro Video | 77 core presets | 4K | Video-transition library, Alien Visits; six separately installed HD Worlds give 83 playable presets |

All editions share the musical Adaptive engine and persistent music playlists. Optional HD Worlds are not embedded in the main Pro Video download. Free and Pro do not include Pro Video-only video assets or optional worlds.

## DRM-free licence and your exports

Free is freely downloadable proprietary software. Pro and Pro Video are ordinary macOS downloads following a one-time purchase: use your edition indefinitely, with no subscription, licence expiry or renewal. Install it on unlimited computers you personally own or use for your own personal and professional work, including work for clients or an employer. This is an individual licence, not a shared or organisation-wide licence for other users. There are no serial numbers, licence keys, online activation, account login, device registration or licence-management software. Once downloaded and installed, Player works offline without contacting a licensing server. Simply install and use your edition; its edition-specific features still apply.

You may create, publish, perform, distribute, sell and monetise finished visual exports containing the bundled presets and HD Worlds, worldwide, perpetually, without royalties or attribution. These rights do not depend on an account, subscription or continued use of Player; completed exports remain usable after uninstalling it. You still need rights to any music or other material you supply. The software and underlying resource libraries remain proprietary and cannot be redistributed or resold without permission. See the accompanying licence and Third-party Notices.

## Install and launch

1. Download your edition from the official website. Use the final release's SHA-256 checksum list when verifying a download; development candidates are not public distributions.
2. Extract the application ZIP with Finder, then drag the application into Applications. If supplied on a disk image, mount it and follow the included installation instructions. Keep each edition's existing application name.
3. Open the application. The initial shader-loading screen can take time, especially on first launch. Use the application menu → About to check the edition, **1.0.0 (build 2)** and website link.

Use official signed/notarised releases. If macOS reports damage, an unidentified developer or an unverified download, stop and check the source, checksum and current support information. Re-download the correct release if needed. Do not disable Gatekeeper or remove quarantine as an installation procedure. Offline first launch is supported only after the final distributed artifact has passed offline release testing.

## Music and playlists

Use **Add Tracks** or **Add Folder** in Music Playlists to import local music. Select a track and press Play. New Playlist, Rename, Delete, shuffle and repeat organise playback. Importing music references your files; keep external drives connected and avoid deleting or moving the originals. Missing tracks can be located again using the recovery controls.

Open **Options → Default Playlist** to choose the music playlist used at startup. Renaming that playlist preserves its identity. Playlist restoration does not automatically start audio playback.

Free, Pro and Pro Video intentionally share playlist data under:

`~/Library/Application Support/Cyanescent Player/`

The principal files are `music-playlists-v1.json` and `music-playlists-v1.backup.json`; additional conflict/unsaved files can preserve recovery data. Quit all editions before making a backup. Do not edit these files while Player is running or delete them when uninstalling only one edition. Music files themselves remain in their original locations.

## Visuals and Adaptive playback

Choose a preset from the Preset menu or use Preset Manager to organise a visual preset playlist. In Options, **Transition Mode → Adaptive** times changes to the music; **Adaptive Time** changes the typical time spent in a preset. Manual preset selection remains available. Local Player Audio can analyse the full track; live input responds to currently arriving audio.

All editions provide rendered transitions. Pro Video additionally offers **Use Video Transitions** and Alien Visits. These are separate options; optional worlds must be validly installed before they become selectable. Standard quality is a useful first performance check.

**Visualiser Fullscreen** opens the separate visualiser window. Cmd+W closes the current window; the Player can remain running. Use the Dock icon or Window → Show Main Player to reopen it. Cmd+Q quits the application and safely handles active export work.

## Export Studio

Load a track, then choose **Export Music Video**. Use **Automatic** for a music-directed visual sequence or **Custom Timeline** to place and edit preset changes. Choose the music range, destination, resolution and frame rate offered by your edition; preview the sequence before a long render. Free exports up to 1080p; Pro and Pro Video offer up to 4K. An unavailable HD World cannot be used in an export.

Select an output location with sufficient free space and start the export. Wait for completion before moving the file. Use the provided cancellation controls if you need to stop; avoid force-quitting during output finalisation. Short draft exports are a useful check before a full-length video.

## HD Worlds

See [HD World installation](V1_HD_WORLD_INSTALLATION.md). Each world is a separate installer app on a disk image. Quit Pro Video, open the installer, click Install World and wait for success, then open/restart Pro Video. No Terminal or copying to Application Support is required. Free and Pro cannot use these worlds.

## Pocket Scion and live audio

Connect a compatible Pocket Scion/SCÍON USB-MIDI device with a data-capable cable and confirm it appears in macOS Audio MIDI Setup. Open **Options → Audio Source → Scion Mode**. Enable the input meter and select the desired sound mode, such as Ethereal Drone or Crystal Chimes; use a comfortable output volume. A connected device with no signal is different from a device actively sending notes/controllers. Check the displayed status if the meter is silent.

For microphone or audio-interface input, choose **Enable External Audio Inputs…**, approve the input request and select the intended device. On macOS 14.2+, **System Audio** captures another application's sound while leaving it audible through the selected output. Earlier macOS versions require a separately configured external/loopback input for that use; a default microphone is not system audio. Third-party routing drivers are not included.

If input is silent, check the selected source, device connection, gain and the source application's playback. In System Settings → Privacy & Security, review Microphone access for external capture, or Screen & System Audio Recording access for native system capture; names vary by macOS version. Quit/reopen Player if macOS requires it after changing permission. System-audio permission and microphone permission are distinct. Scion USB-MIDI input does not itself require microphone capture permission. Do not repeatedly reset all permissions as a first troubleshooting step.

## Troubleshooting and removal

For visual stalls, allow first-load compilation to finish, try Standard quality, close unnecessary GPU-heavy applications and check current support information. For missing music or worlds, reconnect the drive or use the appropriate recovery/reinstallation path. Include the edition, About version/build, macOS version and a description of the problem when seeking support. Never send passwords, private keys or unreviewed playlist files/logs containing personal paths.

To uninstall an edition, quit it and move only its application from Applications to the Bin. Keep shared Application Support data if another edition will still use it. Uninstall individual worlds using the focused guide; their files are separate from music playlists. Clearing macOS WebKit preferences/storage or deleting shared user data is a separate, deliberate reset, not part of ordinary app removal.
