# V1 launch — publication steps

Two launch stages, each with its own check:

- **Pre-commerce public launch** (site live, Free download on, Pro checkout
  deliberately off, Pro Video coming soon):
  `python3 tools/check-site.py --stage precommerce`
- **Full commercial launch** (live checkout and verified purchase download):
  `python3 tools/check-site.py --stage commercial --purchase-verified <sha256 of the ZIP from a real purchase>`

The `v1-launch` branch holds the Cyanescent Player 1.0 site. GitHub Pages
builds `main` from the repository root (legacy build), so **merging to `main`
and pushing is the deployment**. Nothing in this branch is live until then.

## 0. Release readiness

| Item | State |
|---|---|
| Free ZIP `Cyanescent-Player-Free-1.0.0-macOS-universal.zip`, 7,661,960 bytes, SHA-256 `f0da79ba2373dcb0d64a99fa7c669e18d0129150c6874091f2cf5368c66d0b05` | Notarised (Accepted), stapled, locally validated. **Awaiting owner acceptance** |
| Pro ZIP `Cyanescent-Player-Pro-1.0.0-macOS-universal.zip`, 20,350,786 bytes, SHA-256 `1eb6609b6228d542360d22f4408cecd97f6f034bf3558f3ef9ebfd6b31b39c61` (notary UUID `f1fee120-3363-415e-92b5-830f4a5798ae`) | Notarised (Accepted), stapled, Gatekeeper/translocation and 4K export smoke passed. **Awaiting owner acceptance** |
| Physical offline first launch, fresh-machine install, Intel/macOS 12 | **Not yet tested.** The site says "works offline" (EULA wording): run the offline test before launch |
| Pro Video and HD Worlds | Deliberately postponed. Coming soon on the site; no checkout or download |

Checklist before deploying:

- [ ] Owner accepts the exact Free and Pro ZIPs above (re-hash before upload).
- [ ] Offline first-launch test done (or the "works offline" wording changed).
- [ ] Lemon Squeezy store approved and the Pro product set up per
      `_launch/PRO-CHECKOUT-LEMON-SQUEEZY.md` (kept out of git).
- [ ] Refund policy approved, a support contact chosen, and UK/EU cancellation
      consent handling confirmed with Lemon Squeezy.

## 1. Free download (hosted with the site)

The verified Free ZIP from release tag `v1.0.0` (`5bc3150`) is committed at
`downloads/Cyanescent-Player-Free-1.0.0-macOS-universal.zip` (7,661,960 bytes,
SHA-256 `f0da79ba2373dcb0d64a99fa7c669e18d0129150c6874091f2cf5368c66d0b05`) with
`downloads/SHA256SUMS.txt`. GitHub Pages publishes it together with the site, so
it goes live only when the site is deployed. `check-site.py` re-verifies its hash.
After deploying, verify the public copy:

```bash
curl -L -o /tmp/free-check.zip https://cyanescent-dev.github.io/downloads/Cyanescent-Player-Free-1.0.0-macOS-universal.zip
shasum -a 256 /tmp/free-check.zip   # must print f0da79ba…0b05
```

The Pro ZIP is **never** committed here (`check-site.py` fails if any Pro, Pro Video
or HD World archive appears). It's delivered only by Lemon Squeezy.

## 2. Pro checkout (Lemon Squeezy)

1. Upload `build/v1-final-20261023/distribution/Cyanescent-Player-Pro-1.0.0-macOS-universal.zip`
   to the Pro product and confirm the size shown is 20,350,786 bytes.
2. Test mode: check payment, receipt and thank-you page. Test mode may not
   deliver a real file, so don't treat it as the download test.
3. Live delivery test, **with explicit owner approval**: one controlled live
   purchase (e.g. a 100% owner discount code, if the store allows it), download
   from the receipt link, `shasum -a 256` = `1eb6609b…1b39c61`, open in Finder.
   Refund it afterwards if a real payment was taken.
4. Copy the live hosted checkout URL (`https://<store>.lemonsqueezy.com/buy/…`).

## 3. Insert the checkout link and ungate

Use the **live** hosted checkout link from Lemon Squeezy (Products → Cyanescent
Player Pro → Share). It has the form `https://cyanescent.lemonsqueezy.com/buy/<uuid>`
(or `/checkout/buy/<uuid>`), with no query parameters.

```bash
python3 tools/set-checkout-url.py https://cyanescent.lemonsqueezy.com/buy/<uuid>
```

For local testing with a test-mode link, use `--test` instead. The launch check
refuses to pass while a test link is present. Undo with `--reset`.

Support route (owner decision, 24 Oct 2026): **GitHub Issues only**. The Support
page already says so and warns that issues are public. The refund wording stays
gated: it needs a *private* way for buyers to request a refund (e.g. the store
contact Lemon Squeezy shows on receipts), because order details must not be
posted in public issues. Once that route and the wording are approved, edit `support.html`:
add the contact, then delete the `pending-note` paragraph and the
`data-launch-pending="refund-policy"` attribute.

```bash
python3 tools/check-site.py --stage commercial --purchase-verified <sha256>   # must report 0 errors
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
