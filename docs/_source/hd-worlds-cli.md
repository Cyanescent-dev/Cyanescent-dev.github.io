# V1 optional HD Worlds — command-line fallback

## Installing a pack

1. Download only the desired ZIP and its SHA-256 checksum. Optionally check the archive with `shasum -a 256 <archive.zip>` against the published checksum.
2. Quit Cyanescent Player Pro Video completely. Extract the ZIP with Finder; keep the extracted world folder intact.
3. In Terminal, run the installed Pro Video executable, replacing the final path with the extracted world directory:

```sh
"/Applications/Cyanescent Player Pro Video.app/Contents/MacOS/CyanescentPlayerProVideo" --install-hd-world "/path/to/helix-tunnel"
```

For replacement, add `--replace`. The installer validates the source, copies only approved files into a private folder on the destination filesystem, validates the copied files, then atomically publishes them. A failed validation leaves the current installation intact. Replacement atomically swaps directories and retains the previous world as `.previous-<directory>-<UUID>` under HD Worlds; the command prints its location. Once satisfied with the replacement, quit Player and delete that backup manually to recover space. Allow space for the ZIP, extracted source, new installed copy and any retained backup.

4. Restart Player. A valid world becomes selectable. Missing worlds remain visible and disabled as **HD World — Not Installed**; invalid worlds show the validation reason. To uninstall, quit Player, remove only that world's installed directory, and restart.

Installed directories are direct children of:

```text
~/Library/Application Support/Cyanescent Player/HD Worlds/
```

Do not merge packs manually, change files while Player is running, or put expansion data inside the application bundle. No administrator access, account, downloader or licence activation is involved. The CLI requires Pro Video and rejects installation while the standard Pro Video application is running.

