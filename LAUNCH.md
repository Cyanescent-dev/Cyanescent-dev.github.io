# V1 launch — publication steps

The `v1-launch` branch holds the Cyanescent Player 1.0 site. GitHub Pages
builds `main` from the repository root (legacy build), so **merging to `main`
and pushing is the deployment**. Nothing in this branch is live until then.

## 0. Before you start

- [ ] Owner approves the V1 launch and this site.
- [ ] Free ZIP accepted: `Cyanescent-Player-Free-1.0.0-macOS-universal.zip`,
      7,643,421 bytes, SHA-256
      `e62bbb934a209f318cd49e318f6840e9e82f5fc15b26d8424fd67e80729efcc7`.
- [ ] Pro ZIP notarised, stapled and accepted, with its final SHA-256.
- [ ] Checkout product created, tested in the provider's test mode, and
      delivering the exact accepted Pro ZIP.
- [ ] Seller, purchase, refund and cancellation disclosures confirmed for the
      checkout provider.

## 1. Publish the Free download

Upload the accepted ZIP and checksum list as a GitHub release (draft first,
so nothing is public until you publish it):

```bash
cd "$HOME/Documents/Projects/Cyanescent Player/build/job12-free-release/distribution"
gh release create v1.0.0 --repo Cyanescent-dev/Cyanescent-Player --draft \
  --title "Cyanescent Player 1.0.0" \
  --notes "Cyanescent Player Free 1.0.0 for macOS 12+ (universal). See https://cyanescent-dev.github.io" \
  Cyanescent-Player-Free-1.0.0-macOS-universal.zip SHA256SUMS.txt
```

Publish the draft when you are ready, then verify the **public** file:

```bash
curl -L -o /tmp/free-check.zip \
  https://github.com/Cyanescent-dev/Cyanescent-Player/releases/download/v1.0.0/Cyanescent-Player-Free-1.0.0-macOS-universal.zip
shasum -a 256 /tmp/free-check.zip   # must print e62bbb93…efcc7
```

## 2. Activate the buttons in `index.html`

Search for `data-launch-pending`. There are two buttons and two notes.

- Free button: add `href="<verified public ZIP URL>"`, delete `role="link"`,
  `aria-disabled="true"` and `data-launch-pending="free-download"`, and delete
  the `<span … data-launch-pending="free-download-note">` line.
- Pro button: add `href="<verified checkout URL>"`, delete the same three
  attributes, and delete the `pro-checkout-note` line. If you have the Pro
  checksum, add it to the Pro card's `<dl>` the same way as Free's.

Then:

```bash
python3 tools/check-site.py --launch   # must report 0 errors
```

## 3. Preview locally, then deploy

```bash
python3 -m http.server 4173   # open http://localhost:4173
```

Test both buttons for real (download the Free ZIP; open the checkout page),
then deploy:

```bash
git switch main
git merge --ff-only v1-launch   # or a reviewed merge commit
git push origin main
```

Pages rebuilds in about a minute. Check https://cyanescent-dev.github.io/,
`/psy-roller/`, `/docs/licence.html` and both buttons on the live site.

## 4. Legacy 0.9 surfaces (separate approval, after launch)

The new site no longer links 0.9 Preview or Fungal Edition, but these stay
reachable elsewhere. Do not delete release assets. Recommended at launch:

- Publishing the `v1.0.0` release makes it "Latest" in
  Cyanescent-dev/Cyanescent-Player, in place of the Fungal Edition.
- Edit the `v0.9preview` and `V0.9-Fungal-Edition` release notes to say they
  are superseded by 1.0.0 and link to the site; mark Fungal Edition as a
  pre-release.
- Update the Cyanescent-Player repository README, which still promotes
  0.9, to point to the site.
- The Cyanescent-Player repository also serves an old project site at
  https://cyanescent-dev.github.io/Cyanescent-Player/ . Replace its
  `index.html` with a short page that links to (or `meta refresh`es to)
  https://cyanescent-dev.github.io/ .

## Rebuilding pages and images

- Documentation pages: `python3 tools/build-docs.py` (renders
  `docs/_source/*.md`, which must match `docs/_source/SHA256SUMS.txt`).
- New screenshots: `tools/capture-v1-screenshots.sh`, then
  `tools/prepare-image.sh <frame.png> <name>`.
