# Cyanescent — Website

The official website for **Cyanescent Player 1.0** (Free, Pro and the upcoming
Pro Video), plus the **Psy-Roller** plugin page. Static HTML/CSS/JS served by
GitHub Pages from the root of `main`; no build step.

## Project Structure

```
Cyanescent Website/
├── index.html              ← Cyanescent Player 1.0 landing page
├── v1.css / v1.js          ← Styles and progressive-enhancement scripts for the V1 pages
├── support.html, privacy.html
├── docs/                   ← Quick Start, EULA, notices, HD World guide (generated)
│   └── _source/            ← Approved release Markdown (byte-identical, checksummed)
├── assets/v1/              ← Optimised V1 renderer captures, Cosmic Eye, icons
├── psy-roller/             ← Psy-Roller page (uses style.css + script.js)
├── style.css / script.js   ← Original site styles; still used by psy-roller/
├── assets/img/, screenshots/ ← 0.9-era media, no longer linked from the V1 pages
├── tools/                  ← check-site.py, build-docs.py, image/capture helpers
└── LAUNCH.md               ← Exact publication steps
```

Before publishing, run `python3 tools/check-site.py --launch` and follow
[LAUNCH.md](LAUNCH.md).

## Local Preview

No build step is needed. Serve the directory with any local HTTP server:

```bash
# Python 3
cd "Cyanescent Website"
python3 -m http.server 8000

# Then open http://localhost:8000
```

Or use the VS Code Live Server extension, or any equivalent.

> **Note:** Opening `index.html` directly from the filesystem (`file://`) may block some features in certain browsers. A local server is recommended.
