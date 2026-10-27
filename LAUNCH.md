# Cyanescent website — launch state and maintenance

**State (27 Oct 2026): full V1 commercial launch.** Free download hosted here;
Pro and Pro Video sold through live Lemon Squeezy hosted checkouts; HD Worlds
are free downloads on the separate HD hosting server.

## Release facts shown on the site (build/V1.0 Notarised/RELEASE_MANIFEST.md)

| Edition | File | Bytes | SHA-256 | Delivery |
|---|---|---:|---|---|
| Free | `Cyanescent-Player-free-1.0.0-build-2-d10b51c-macOS-universal-FINAL.zip` | 7,739,869 | `5802855cd26564598fccecd40ba6baf24c9766ac6c12eab9bcd2253caa954664` | `downloads/` (this site) |
| Pro | `Cyanescent-Player-pro-1.0.0-build-2-d10b51c-macOS-universal-FINAL.zip` | 20,407,080 | `19346048d61960fc50f2518b6877d0abcaad3356daf5851a72e49767c426bf85` | Lemon Squeezy |
| Pro Video | `Cyanescent-Player-pro-video-1.0.0-build-2-228e245-macOS-universal-FINAL.zip` | 1,974,722,085 | `4dee485499b3e53a5d1a211ffb5cc89b8658be00475bd8e10fb4a8b86c0e5568` | Lemon Squeezy |
| HD Worlds (6 DMGs) | see the HD release manifest | 0.41–2.53 GB each | hosted SHA256SUMS.txt | https://132.145.31.40.sslip.io/downloads/cyanescent/hd-worlds.html |

Checkouts (supplied by the store owner; never replace with test-mode links):

- Pro ($5, regular $15): https://cyanescent.lemonsqueezy.com/checkout/buy/1d36466c-93bf-4019-ba51-ee53cd6b783d
- Pro Video ($30): https://cyanescent.lemonsqueezy.com/checkout/buy/e1ccdd99-cb67-4d79-9869-3b983bb1122e

Paid ZIPs and HD World DMGs are never committed here; `tools/check-site.py`
fails if one appears, and only these two exact checkout URLs are allowed.

## Checks and deploy

```bash
python3 tools/check-site.py --stage commercial          # deploy gate (0 errors)
git switch main && git merge --ff-only v1-launch && git push origin main
```

GitHub Pages builds `main` from the repository root (legacy build). After a
supervised purchase of each paid edition, record it:

```bash
python3 tools/check-site.py --stage commercial \
  --purchase-verified <sha256 of the Pro ZIP from the purchase> \
  --purchase-verified-pro-video <sha256 of the Pro Video ZIP from the purchase>
```

## Changing a price or checkout

Edit the `CHECKOUT` URLs in `tools/check-site.py` and the matching `href`s in
`index.html` together (buttons carry `data-checkout="pro"` or `"pro-video"`).

## Rebuilding pages and images

- Documentation: `python3 tools/build-docs.py` (renders `docs/_source/*.md`,
  which must match `docs/_source/SHA256SUMS.txt`).
- Images: `tools/prepare-image.sh <screenshot.png> <name> [top-crop-px]`.
