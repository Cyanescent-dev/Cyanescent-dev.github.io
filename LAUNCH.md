# V1 launch — publication steps

The `v1-launch` branch holds the Cyanescent Player 1.0 site. GitHub Pages
builds `main` from the repository root (legacy build), so **merging to `main`
and pushing is the deployment**. Nothing in this branch is live until then.

## 0. Release readiness

| Item | State |
|---|---|
| Free ZIP `Cyanescent-Player-Free-1.0.0-macOS-universal.zip`, 7,643,421 bytes, SHA-256 `e62bbb934a209f318cd49e318f6840e9e82f5fc15b26d8424fd67e80729efcc7` | Notarised (Accepted), stapled, locally validated. **Awaiting owner acceptance** |
| Pro ZIP `Cyanescent-Player-Pro-1.0.0-macOS-universal.zip`, 20,310,870 bytes, SHA-256 `3619a69083bd35249cb1ae4e8a6041c20a29c281e8baed4264bef4904d384370` (notary UUID `ca383470-b1e6-46e5-9e84-46cb9e0b8099`) | Notarised (Accepted), stapled, Gatekeeper/translocation and 4K export smoke passed. **Awaiting owner acceptance** |
| Physical offline first launch, fresh-machine install, Intel/macOS 12 | **Not yet tested.** The site says "works offline" (EULA wording): run the offline test before launch |
| Pro Video and HD Worlds | Deliberately postponed. Coming soon on the site; no checkout or download |

Checklist before deploying:

- [ ] Owner accepts the exact Free and Pro ZIPs above (re-hash before upload).
- [ ] Offline first-launch test done (or the "works offline" wording changed).
- [ ] Lemon Squeezy store approved and the Pro product set up per
      `_launch/PRO-CHECKOUT-LEMON-SQUEEZY.md` (kept out of git).
- [ ] Refund policy approved, a support contact chosen, and UK/EU cancellation
      consent handling confirmed with Lemon Squeezy.

## 1. Publish the Free download

Upload the accepted ZIP and checksum list as a GitHub release (draft first,
so nothing is public until you publish it):

```bash
cd "$HOME/Documents/Projects/Cyanescent Player/build/job12-free-release/distribution"
shasum -a 256 Cyanescent-Player-Free-1.0.0-macOS-universal.zip   # e62bbb93…efcc7
gh release create v1.0.0 --repo Cyanescent-dev/Cyanescent-Player --draft \
  --title "Cyanescent Player 1.0.0" \
  --notes "Cyanescent Player Free 1.0.0 for macOS 12+ (universal). Pro: https://cyanescent-dev.github.io/#editions" \
  Cyanescent-Player-Free-1.0.0-macOS-universal.zip SHA256SUMS.txt
```

Publish the draft when you are ready, then verify the **public** file:

```bash
curl -L -o /tmp/free-check.zip \
  https://github.com/Cyanescent-dev/Cyanescent-Player/releases/download/v1.0.0/Cyanescent-Player-Free-1.0.0-macOS-universal.zip
shasum -a 256 /tmp/free-check.zip   # must print e62bbb93…efcc7
```

The Pro ZIP is **not** uploaded to GitHub. It's delivered only by Lemon Squeezy.

## 2. Pro checkout (Lemon Squeezy)

1. Upload `build/job13-pro-release/distribution/Cyanescent-Player-Pro-1.0.0-macOS-universal.zip`
   to the Pro product and confirm the size shown is 20,310,870 bytes.
2. Test mode: check payment, receipt and thank-you page. Test mode may not
   deliver a real file, so don't treat it as the download test.
3. Live delivery test, **with explicit owner approval**: one controlled live
   purchase (e.g. a 100% owner discount code, if the store allows it), download
   from the receipt link, `shasum -a 256` = `3619a690…4384370`, open in Finder.
   Refund it afterwards if a real payment was taken.
4. Copy the live hosted checkout URL (`https://<store>.lemonsqueezy.com/buy/…`).

## 3. Activate the gated controls

Search for `data-launch-pending`. There are four in `index.html` and one in `support.html`.

- Free button: add `href="<verified public ZIP URL>"`, delete `role="link"`,
  `aria-disabled="true"` and `data-launch-pending="free-download"`, and delete
  the `free-download-note` line.
- Pro button: add `href="<live checkout URL>"`, delete the same three attributes,
  and delete the `pro-checkout-note` line.
- `support.html`: once the refund wording is approved, add the support contact,
  delete the `pending-note` paragraph and the `data-launch-pending` attribute.

Then:

```bash
python3 tools/check-site.py --launch   # must report 0 errors
```

## 4. Preview locally, then deploy

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
`/psy-roller/`, `/docs/licence.html`, the Milkrunner and Psy-Roller downloads,
and both buttons on the live site.

## 5. Legacy 0.9 surfaces (separate approval, right after deploying)

Prepared, not applied: `_launch/legacy/proposed/` with `APPLY.md`. It
covers superseded notices for both 0.9 releases (Fungal Edition stops being
"Latest"), a V1 README for the distribution repository, a "moved" page for
https://cyanescent-dev.github.io/Cyanescent-Player/ , and the checksum list.
No release, tag or binary is deleted.

## 6. Later

- Ending the launch price: change Lemon Squeezy to $15 **and** update the site
  copy in the same session.
- Pro Video and HD Worlds: separate release once notarisation uploads are possible.
- Optional crypto payments: explore after launch; no custom backend.

## Rebuilding pages and images

- Documentation pages: `python3 tools/build-docs.py` (renders
  `docs/_source/*.md`, which must match `docs/_source/SHA256SUMS.txt`).
- New screenshots: `tools/prepare-image.sh <screenshot.png> <name> [top-crop-px]`
  (trims a black top bar, keeps the aspect ratio, writes JPEG + AVIF).
