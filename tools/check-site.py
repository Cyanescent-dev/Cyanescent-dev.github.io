#!/usr/bin/env python3
"""Pre-publication checks for the Cyanescent website.

  python3 tools/check-site.py                         # preview: pending items are warnings
  python3 tools/check-site.py --stage commercial      # deploy gate for the live store
  python3 tools/check-site.py --stage commercial \
      --purchase-verified <sha256 of Pro ZIP from a real purchase> \
      --purchase-verified-pro-video <sha256 of Pro Video ZIP from a real purchase>
                                                      # records end-to-end purchase verification
  (--launch is an alias for --stage commercial)

Checks every local page for broken internal links, anchors and images,
oversized media, retired 0.9 download links, checkout links (only the two
approved live Lemon Squeezy URLs, on the matching product's buttons),
misleading activation/licensing wording, the published edition facts, the
hosted Free ZIP's checksum, that no paid or unreleased archive is in the
site, and that Psy-Roller is unchanged from main.
"""

import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlparse

ROOT = Path(__file__).resolve().parent.parent
def _arg(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
    return None

STAGE = _arg("--stage") or ("commercial" if "--launch" in sys.argv else "preview")
if STAGE not in ("preview", "commercial"):
    sys.exit(f"unknown stage {STAGE!r}")
LAUNCH = STAGE != "preview"

# Final V1 release (build/V1.0 Notarised/RELEASE_MANIFEST.md).
PRO_SHA256 = "19346048d61960fc50f2518b6877d0abcaad3356daf5851a72e49767c426bf85"
PRO_VIDEO_SHA256 = "4dee485499b3e53a5d1a211ffb5cc89b8658be00475bd8e10fb4a8b86c0e5568"
# Live Lemon Squeezy hosted checkouts supplied by the store owner.
CHECKOUT = {
    "pro": "https://cyanescent.lemonsqueezy.com/checkout/buy/1d36466c-93bf-4019-ba51-ee53cd6b783d",
    "pro-video": "https://cyanescent.lemonsqueezy.com/checkout/buy/e1ccdd99-cb67-4d79-9869-3b983bb1122e",
}
HD_WORLDS_PAGE = "https://132.145.31.40.sslip.io/downloads/cyanescent/hd-worlds.html"
PAGES = sorted(
    p for p in ROOT.rglob("*.html")
    if not {".git", "_source", "_launch"} & set(p.parts)
)
MAX_IMAGE_BYTES = 400_000
FREE_ZIP = "downloads/Cyanescent-Player-free-1.0.0-build-2-d10b51c-macOS-universal-FINAL.zip"
FREE_SHA256 = "5802855cd26564598fccecd40ba6baf24c9766ac6c12eab9bcd2253caa954664"

errors, warnings = [], []


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.refs, self.pending, self.links = set(), [], [], []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for key in ("href", "src", "data-full", "poster"):
            if a.get(key):
                self.refs.append((tag, a[key]))
        for key in ("srcset",):
            if a.get(key):
                for part in a[key].split(","):
                    self.refs.append((tag, part.strip().split()[0]))
        if "data-launch-pending" in a:
            self.pending.append(a["data-launch-pending"])
        if tag == "a":
            self.links.append((a.get("href", ""), list(self.stack)))
        if tag in ("section", "article"):
            self.stack.append(a.get("id", ""))

    def handle_endtag(self, tag):
        if tag in ("section", "article") and self.stack:
            self.stack.pop()


parsed = {}
for path in PAGES:
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    parsed[path] = p

# 1. Internal links, anchors and media
for path, p in parsed.items():
    rel = path.relative_to(ROOT)
    for tag, ref in p.refs:
        url = urlparse(ref)
        if url.scheme in ("http", "https", "mailto", "data"):
            continue
        target_ref, frag = urldefrag(ref)
        if target_ref == "":
            target = path
        else:
            target = (path.parent / target_ref).resolve()
            if target.is_dir():
                target = target / "index.html"
        if not target.exists():
            errors.append(f"{rel}: broken {tag} reference {ref}")
            continue
        if frag and target.suffix == ".html":
            if frag not in parsed.get(target, Page()).ids:
                errors.append(f"{rel}: missing anchor #{frag} in {target.relative_to(ROOT)}")
        if target.suffix.lower() in (".mp4", ".m4v", ".mov", ".webm"):
            size = target.stat().st_size
            if size > 100_000_000:
                errors.append(f"{rel}: {ref} is {size:,} bytes; GitHub rejects files over 100 MB")
        if target.suffix.lower() in (".jpg", ".jpeg", ".png", ".avif", ".webp", ".gif"):
            size = target.stat().st_size
            if size > MAX_IMAGE_BYTES:
                warnings.append(f"{rel}: {ref} is {size:,} bytes (> {MAX_IMAGE_BYTES:,})")

# 2. Retired downloads and development builds must not be linked
RETIRED = [
    r"v0\.9preview", r"V0\.9-Fungal-Edition", r"Cyanescent-Player-0\.9", r"Fungal-0\.9",
    r"/build/", r"job1[23]-", r"submission\.zip", r"candidate", r"localhost", r"127\.0\.0\.1",
]
for path in PAGES:
    if path.parts[-2] == "psy-roller":
        continue
    text = path.read_text(encoding="utf-8")
    for href in re.findall(r'href="([^"]+)"', text):
        for pattern in RETIRED:
            if re.search(pattern, href):
                errors.append(f"{path.relative_to(ROOT)}: retired or development link {href}")

# 3. Paid editions are never linked as files: only via the approved checkout or HD Worlds page
for path, p in parsed.items():
    for href, stack in p.links:
        if re.search(r"(pro|pro-video|hd-world).*\.(zip|dmg|pkg)$", href, re.I):
            errors.append(f"{path.relative_to(ROOT)}: direct link to a paid or HD World archive {href}")
        if any(s in ("pro-video", "ed-video", "buy-pro-video") for s in stack) and href.startswith("http"):
            if href not in (CHECKOUT["pro-video"], HD_WORLDS_PAGE):
                errors.append(f"{path.relative_to(ROOT)}: unexpected outbound link in Pro Video content {href}")

# 4. Misleading licensing language (approved EULA wording is exempt)
MISLEADING = [
    r"licen[cs]e key (is )?required", r"enter your (licen[cs]e|serial|key)", r"activate (your|the) (copy|licen)",
    r"\bopen[- ]source software\b(?! license)", r"subscribe now", r"per[- ]seat", r"lifetime updates",
    r"free forever", r"unlimited users",
]
for path in PAGES:
    if "docs" in path.parts or path.parts[-2] == "psy-roller":
        continue
    text = re.sub(r"<[^>]+>", " ", path.read_text(encoding="utf-8"))
    for pattern in MISLEADING:
        if re.search(pattern, text, re.I):
            errors.append(f"{path.relative_to(ROOT)}: wording matches /{pattern}/")

# 5. Edition facts on the landing page
index = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", (ROOT / "index.html").read_text(encoding="utf-8")))
FACTS = [
    "18 curated", "75 music-responsive presets", "77 core music-responsive presets", "Up to 83 presets",
    "$5", "$15", "$30", "up to 1080p", "up to 4K", "macOS 12 or later", "macOS 14.2",
    FREE_SHA256, "7,739,869 bytes", "Buy once.", "Create forever.",
    PRO_SHA256, "20,407,080 bytes", PRO_VIDEO_SHA256, "1,974,722,085 bytes",
    "Launch price $5 — regular price $15", "Lemon Squeezy", "Get Pro Video — $30",
    "Adaptive Synesthesia Engine", "Alien Visits", "HD Worlds download page",
    "Milkrunner", "Psy-Roller",
]
for fact in FACTS:
    if fact.lower() not in index.lower():
        errors.append(f"index.html: expected fact missing: {fact!r}")
for wrong in ("Pro Video — $5", "Fungal Edition download", "Coming soon", "not yet available",
              "when released", "will follow Free and Pro", "next edition", "4K transition", "4K video transition"):
    if wrong.lower() in index.lower():
        errors.append(f"index.html: unexpected text {wrong!r}")

# 5b. Rejected or obsolete imagery must not return, and companion downloads must stay
raw_index = (ROOT / "index.html").read_text(encoding="utf-8")
for rejected in ("higher-dimensional-jellyfish", "smuggler-run", "kleinian-coral-cathedral",
                 "assets/img/", "fungal-preset"):
    if rejected in raw_index:
        errors.append(f"index.html: rejected/obsolete image referenced: {rejected}")
for required in (
    "https://github.com/Cyanescent-dev/milkrunner/releases/download/milk-runner-visuals/Milk.Runner.Visualizer.zip",
    "https://github.com/Cyanescent-dev/Cyanescent-dev.github.io/releases/download/psy-roller-v1.0.1/Psy-Roller-1.0.1-VST3.zip",
    'href="psy-roller/"',
):
    if required not in raw_index:
        errors.append(f"index.html: companion product link missing: {required}")

# 5c. Release artifacts: only the verified Free ZIP may be hosted here
import hashlib
free = ROOT / FREE_ZIP
if not free.exists():
    errors.append(f"missing hosted Free download {FREE_ZIP}")
elif hashlib.sha256(free.read_bytes()).hexdigest() != FREE_SHA256:
    errors.append(f"{FREE_ZIP} does not match the verified SHA-256")
for f in ROOT.rglob("*"):
    if ".git" in f.parts or not f.is_file():
        continue
    name = f.name.lower()
    if re.search(r"(pro|pro-video|hd-world|submission).*\.(zip|dmg|pkg)$", name) or name.endswith(".dmg"):
        errors.append(f"paid or unreleased artifact present in the site: {f.relative_to(ROOT)}")
    if f.stat().st_size > 100_000_000:
        errors.append(f"{f.relative_to(ROOT)} exceeds GitHub's 100 MB file limit")

# 5d. Checkout links: only the two approved live hosted checkouts, on matching buttons
for path in PAGES:
    raw = path.read_text(encoding="utf-8")
    for tag in re.findall(r"<a\b[^>]*>", raw):
        href = re.search(r'href="([^"]+)"', tag)
        kind = re.search(r'data-checkout="([^"]+)"', tag)
        if kind and kind.group(1) == "test":
            errors.append(f"{path.relative_to(ROOT)}: TEST checkout link; never deploy it")
        if href and "lemonsqueezy.com" in href.group(1):
            if href.group(1) not in CHECKOUT.values():
                errors.append(f"{path.relative_to(ROOT)}: unapproved checkout URL {href.group(1)}")
            elif not kind or CHECKOUT.get(kind.group(1)) != href.group(1):
                errors.append(f"{path.relative_to(ROOT)}: checkout URL on a button for the wrong product: {tag[:90]}")
        if kind and kind.group(1) in CHECKOUT and (not href or href.group(1) != CHECKOUT[kind.group(1)]):
            errors.append(f"{path.relative_to(ROOT)}: {kind.group(1)} button without its live checkout URL")
for label, kind in (("Get Pro — $5", "pro"), ("Get Pro Video — $30", "pro-video")):
    for m in re.finditer(r"<a\b([^>]*)>([^<]*)</a>", raw_index):
        if m.group(2).strip() == label and f'href="{CHECKOUT[kind]}"' not in m.group(1):
            errors.append(f"index.html: '{label}' button is not linked to its live checkout")
    if raw_index.count(f'href="{CHECKOUT[kind]}"') == 0:
        errors.append(f"index.html: no {kind} checkout link")
if STAGE == "commercial":
    for flag, kind, sha in (("--purchase-verified", "Pro", PRO_SHA256),
                            ("--purchase-verified-pro-video", "Pro Video", PRO_VIDEO_SHA256)):
        given = _arg(flag)
        if given is None:
            warnings.append(f"commercial: {kind} end-to-end purchase not yet verified ({flag} <sha256>)")
        elif given != sha:
            errors.append(f"commercial: {flag} does not match the released {kind} SHA-256")

# 6. Launch-pending controls
for path, p in parsed.items():
    for name in p.pending:
        msg = f"{path.relative_to(ROOT)}: launch-pending control '{name}'"
        (errors if LAUNCH else warnings).append(msg)

# 7. Psy-Roller and its shared assets unchanged from main
try:
    diff = subprocess.run(
        ["git", "diff", "--stat", "main", "--", "psy-roller", "style.css", "script.js"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()
    if diff:
        errors.append("Psy-Roller page or its shared style.css/script.js differ from main:\n" + diff)
except (subprocess.CalledProcessError, FileNotFoundError) as exc:
    warnings.append(f"could not compare Psy-Roller with main: {exc}")

for w in warnings:
    print(f"warning: {w}")
for e in errors:
    print(f"ERROR: {e}")
print(f"\n{len(PAGES)} pages checked · {len(errors)} errors · {len(warnings)} warnings"
      f" · stage: {STAGE}")
sys.exit(1 if errors else 0)
