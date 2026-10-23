#!/usr/bin/env python3
"""Pre-publication checks for the Cyanescent website.

  python3 tools/check-site.py            # preview: pending launch links are warnings
  python3 tools/check-site.py --launch   # launch: pending launch links are errors

Checks every local page for broken internal links, anchors and images,
oversized media, retired 0.9 download links, any Pro Video checkout or
download, misleading activation/licensing wording, the published edition
facts, and that Psy-Roller is unchanged from main.
"""

import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlparse

ROOT = Path(__file__).resolve().parent.parent
LAUNCH = "--launch" in sys.argv
PAGES = sorted(
    p for p in ROOT.rglob("*.html")
    if not {".git", "_source", "_launch"} & set(p.parts)
)
MAX_IMAGE_BYTES = 400_000
FREE_ZIP = "downloads/Cyanescent-Player-Free-1.0.0-macOS-universal.zip"
FREE_SHA256 = "f0da79ba2373dcb0d64a99fa7c669e18d0129150c6874091f2cf5368c66d0b05"

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

# 3. Pro Video must have no checkout or download
for path, p in parsed.items():
    for href, stack in p.links:
        if any(s in ("pro-video", "ed-video") for s in stack):
            if href.startswith("http") or re.search(r"\.(zip|dmg|pkg)$", href):
                errors.append(f"{path.relative_to(ROOT)}: Pro Video has an outbound/download link {href}")
    text = path.read_text(encoding="utf-8")
    if re.search(r"Pro-?Video[^\"]*\.(zip|dmg)", text, re.I) and "hd-worlds" not in path.name:
        errors.append(f"{path.relative_to(ROOT)}: a Pro Video download filename is linked or named")

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
    "18 curated", "75 real-time visual presets", "77 core presets", "Up to 83 presets",
    "$5", "$15", "$30", "up to 1080p", "up to 4K", "macOS 12 or later", "macOS 14.2",
    "Not yet available to buy", FREE_SHA256, "7,661,960 bytes", "Buy once.", "Create forever.",
    "1eb6609b6228d542360d22f4408cecd97f6f034bf3558f3ef9ebfd6b31b39c61", "20,350,786 bytes",
    "Launch price $5 — regular price $15", "Lemon Squeezy", "Coming soon",
    "Milkrunner", "Psy-Roller",
]
for fact in FACTS:
    if fact.lower() not in index.lower():
        errors.append(f"index.html: expected fact missing: {fact!r}")
for wrong in ("Pro Video — $5", "Get Pro Video", "Buy Pro Video", "Fungal Edition download"):
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

# 5d. Pro checkout link: live Lemon Squeezy hosted checkout only
pro_btn = re.search(r'<a id="pro-checkout"[^>]*>', raw_index)
if not pro_btn:
    errors.append("index.html: #pro-checkout button missing")
else:
    tag = pro_btn.group(0)
    href = re.search(r'href="([^"]+)"', tag)
    if 'data-checkout="test"' in tag:
        (errors if LAUNCH else warnings).append("index.html: Pro button uses a TEST checkout link; never deploy it")
    if href and not re.match(r"^https://cyanescent\.lemonsqueezy\.com/(checkout/)?buy/[0-9a-f-]{36}/?$", href.group(1)):
        errors.append(f"index.html: unexpected Pro checkout URL {href.group(1)}")
    if LAUNCH and not href:
        errors.append("index.html: Pro checkout URL not set (tools/set-checkout-url.py)")

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
      f" · mode: {'launch' if LAUNCH else 'preview'}")
sys.exit(1 if errors else 0)
