# Optional HD Worlds — installation and removal

For **Cyanescent Player Pro Video 1.0.0**. The six worlds are Red Cage Stinkhorn, Physarum, Newton Basin, Newton's Law, Artificial Consciousness and Helix Tunnel. Install only the worlds you want. All six increase Pro Video's 77 core presets to 83 playable presets.

## Install a world

1. Download the world's **Installer 1.0.0** disk image from [the official website](https://cyanescent-dev.github.io). Verify its checksum against the final release list if desired. Keep Player and world versions matched.
2. Quit Cyanescent Player Pro Video completely with Cmd+Q. Closing its window alone does not quit it.
3. Open the DMG in Finder. Double-click the **<World> Installer** application inside it; do not copy the payload or locate an extracted world folder.
4. Check the world name, package size and required Player version. Click **Install World**. The installer checks the package, copies and verifies it, then activates it. Cancel is available before final activation. No administrator password is required.
5. Wait for **installed successfully**, then click Done. Open/restart Pro Video and select the world in the preset collection. Eject the disk image afterward. The optional Open Player button opens the chosen Pro Video application only when you click it.

If Pro Video cannot be found, install it first or use **Choose Pro Video…** to locate your existing 1.0.0 application. Choosing another edition or an incompatible version will not work. The installer never installs another application or terminates Player automatically.

The DMG must be a final signed/notarised release. An unsigned prototype is for acceptance testing and does not establish downloaded Gatekeeper behaviour. Do not disable macOS security to install an unverified download.

## Space, reinstallation and errors

Allow room for the downloaded DMG, a complete new installed copy and any previous copy retained for rollback. Approximate payload sizes are 2.53 GB for Stinkhorn, 0.71 GB for Physarum and 0.41–0.47 GB for each other world. The installer requires the new payload plus a small safety margin to be free **in addition to** existing data.

Running an installer again asks before replacing its world. Replacement keeps the previous copy as a hidden `.previous-<world>-<identifier>` directory; it does not merge files. Keep that backup until the new installation is accepted. Corruption, mismatched metadata, unsafe paths or insufficient disk space produce an error and leave the prior installation intact. Quit Player before retrying.

Ordinary cancellation removes its incomplete private staging copy. Force-quitting or losing power may leave hidden staging/rollback data. Retry is safe, but do not delete hidden installer directories while an installer is active. Seek guidance before reclaiming an unfamiliar hidden directory: it may contain the previous world.

## Find and remove an installed world

Installed worlds live in your account, outside the application:

`~/Library/Application Support/Cyanescent Player/HD Worlds/`

| World | Installed folder |
|---|---|
| Red Cage Stinkhorn | `red-cage-stinkhorn` |
| Physarum | `apollonian-physarum-genesis` |
| Newton Basin | `newton-basin-descent` |
| Newton's Law | `newtons-law` |
| Artificial Consciousness | `artificial-consciousness` |
| Helix Tunnel | `helix-tunnel` |

To remove one world, quit Pro Video and all world installers. In Finder use Go → Go to Folder, enter the location above, and move only that world's folder to the Bin. Restart Player. Missing worlds remain visible but disabled as **HD World — Not Installed**; invalid installations show a validation reason. Removing a world does not remove music or playlists. Do not delete the entire Cyanescent Player Application Support folder.

The older ZIP/command-line mechanism remains a supported fallback and diagnostic path for maintainers; it is described in [the technical HD World guide](V1_HD_WORLDS.md). Customers using installer DMGs do not need Terminal.
