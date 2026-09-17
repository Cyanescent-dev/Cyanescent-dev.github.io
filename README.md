# Cyanescent Player — Release Website

The official one-page release website for the **Cyanescent Player 0.9 Preview**, a native macOS music player and audio-reactive visualiser.

## Project Structure

```
Cyanescent Website/
├── index.html              ← Single-page website
├── style.css               ← All styles (no preprocessor)
├── script.js               ← Minimal vanilla JavaScript
├── README.md               ← This file
├── screenshots/            ← Original source screenshots (do not modify)
└── assets/
    └── img/                ← Web-optimised copies used by the site
```

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

## Replacing the Video Placeholder

1. Place your final video file (e.g. `cyanescent-preview.mp4`) in the `assets/` directory.
2. Open `index.html` and find the `<!-- VIDEO REPLACEMENT INSTRUCTIONS -->` comment in the `#video` section.
3. Replace the `<img class="video-poster" ...>` element with:

   ```html
   <video class="video-poster"
          poster="assets/img/video-poster.jpg"
          controls
          preload="metadata"
          playsinline>
     <source src="assets/cyanescent-preview.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>
   ```

4. Remove the `<div class="video-overlay">...</div>` element.
5. The poster image (`video-poster.jpg`) will display before the video plays.

## Replacing Placeholder URLs

All placeholder URLs are marked in the HTML with:
- `href="#PLACEHOLDER-..."` — easy to search for
- `data-placeholder="true"` — machine-identifiable

Search for `PLACEHOLDER` in `index.html` to find all instances:

| Placeholder | Purpose |
|-------------|---------|
| `#PLACEHOLDER-DOWNLOAD` | macOS download link |
| `#PLACEHOLDER-GITHUB` | GitHub repository URL |
| `#PLACEHOLDER-GITHUB-RELEASES` | GitHub releases page |
| `#PLACEHOLDER-RELEASE-NOTES` | Release notes URL |
| `#PLACEHOLDER-ISSUES` | Issue tracker URL |
| `#PLACEHOLDER-LICENCE` | Licence page URL |
| `#PLACEHOLDER-CREDITS` | Credits page URL |

Also update:
- `<meta property="og:url" ...>` — canonical URL
- `<link rel="canonical" ...>` — canonical URL
- `<meta property="og:image" ...>` — social preview image URL
- Copyright year in the footer

## Screenshot Assets

The `screenshots/` directory contains the original unmodified screenshots. The `assets/img/` directory contains web-optimised JPEG copies used by the site.

If you add or replace screenshots:
1. Place originals in `screenshots/`
2. Create optimised copies using `sips`:
   ```bash
   # For gallery images (1600px wide)
   sips -Z 1600 -s format jpeg -s formatOptions 80 \
     "screenshots/New Screenshot.png" \
     --out "assets/img/new-image.jpg"

   # For hero images (2400px wide)
   sips -Z 2400 -s format jpeg -s formatOptions 82 \
     "screenshots/New Screenshot.png" \
     --out "assets/img/hero-new.jpg"
   ```
3. Update the `src` and `alt` attributes in `index.html`

## GitHub Pages Deployment

The site is designed to be served from the **repository root**.

### Option A: Deploy from repository root

1. Push this directory as the root of a GitHub repository
2. Go to **Settings → Pages**
3. Set **Source** to "Deploy from a branch"
4. Select the **main** branch and **/ (root)** folder
5. Save — the site will be available at `https://username.github.io/repo-name/`

### Option B: Deploy from `/docs` folder

1. Move the website files into a `/docs` folder in your repository
2. Go to **Settings → Pages**
3. Set source to **main** branch, **/docs** folder
4. Save

### Option C: GitHub Actions

Use the default GitHub Pages action for static sites — no configuration needed.

## Technical Notes

- **No framework, no build system** — pure HTML, CSS, and vanilla JavaScript
- **Fonts**: Outfit and Inter loaded from Google Fonts
- **Accessibility**: Semantic HTML, skip link, keyboard navigation, ARIA attributes, focus states, `prefers-reduced-motion` support
- **Performance**: Lazy-loaded images, declared aspect ratios, IntersectionObserver for scroll reveals and animation pausing
- **Browser support**: Modern browsers (Chrome, Firefox, Safari, Edge). The site uses CSS custom properties, `backdrop-filter`, `aspect-ratio`, and `IntersectionObserver`.

## Favicon

The site currently uses a simple SVG data URI favicon. To replace it:
1. Create your favicon files (`.ico`, `.png`, `.svg`)
2. Place them in the root directory
3. Update the `<link rel="icon" ...>` tag in `index.html`
