#!/usr/bin/env python3
"""Render the approved Cyanescent Player 1.0.0 customer documents as site pages.

The Markdown sources in docs/_source/ are byte-identical copies of the
documents shipped inside the release ZIPs (checked against
docs/_source/SHA256SUMS.txt before anything is written). Text is never
edited here; only document-to-document links are rewritten to site URLs.

Usage: python3 tools/build-docs.py
"""

import hashlib
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "_source"
OUT = ROOT / "docs"

PAGES = [
    # (output file, nav label, page title, [source files])
    ("quick-start.html", "Quick Start", "Quick Start", ["quick-start.md"]),
    ("licence.html", "Licence (EULA)", "End-user licence agreement", ["EULA.md"]),
    ("third-party-notices.html", "Third-party notices", "Third-party notices", ["third-party-notices.md"]),
    ("hd-worlds.html", "HD World installation", "HD World installation", ["optional-hd-worlds.md"]),
]

# Site-only notes shown above a document (never inside the approved text).
PREFACE = {
    "hd-worlds.html": (
        '<p class="doc-meta">Download the six optional HD World installers from the '
        '<a href="https://132.145.31.40.sslip.io/downloads/cyanescent/hd-worlds.html" rel="noopener">'
        'HD Worlds download page</a>. They are free for Pro Video owners.</p>'
    ),
}

# Cross-document links inside the approved Markdown, mapped to site pages.
LINKS = {
    "V1_HD_WORLD_INSTALLATION.md": "hd-worlds.html",
    "V1_HD_WORLDS.md": "hd-worlds.html",
    "https://cyanescent-dev.github.io": "../",
}


def verify_sources():
    expected = {}
    for line in (SOURCE / "SHA256SUMS.txt").read_text().splitlines():
        digest, name = line.split(None, 1)
        expected[Path(name).name] = digest
    for name, digest in expected.items():
        actual = hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
        if actual != digest:
            sys.exit(f"{name}: checksum mismatch; refusing to build from an unapproved document")


def slug(text):
    text = re.sub(r"<[^>]+>", "", text).lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def inline(text):
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append(f"<code>{html.escape(part[1:-1])}</code>")
            continue
        part = html.escape(part, quote=False)
        part = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", part)
        part = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", part)

        def link(m):
            label, url = m.group(1), m.group(2)
            url = LINKS.get(url, url)
            external = url.startswith("http")
            rel = ' rel="noopener noreferrer"' if external else ""
            return f'<a href="{html.escape(url)}"{rel}>{label}</a>'

        part = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, part)
        out.append(part)
    return "".join(out)


def render(markdown):
    lines = markdown.splitlines()
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            out.append(f"<pre><code>{html.escape(chr(10).join(body))}</code></pre>")
            continue
        m = re.match(r"(#{1,4})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            content = inline(m.group(2))
            out.append(f'<h{level} id="{slug(content)}">{content}</h{level}>')
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[2:]]
            t = ['<div class="table-wrap"><table><thead><tr>']
            t += [f'<th scope="col">{inline(c)}</th>' for c in head]
            t.append("</tr></thead><tbody>")
            for r in body:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue
        list_match = re.match(r"(\d+\.|-)\s+", line)
        if list_match:
            ordered = list_match.group(1) != "-"
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines):
                m = re.match(r"(\d+\.|-)\s+(.*)", lines[i])
                if m:
                    items.append(m.group(2))
                elif lines[i].startswith("   ") and lines[i].strip() and items:
                    items[-1] += " " + lines[i].strip()
                elif not lines[i].strip() and i + 1 < len(lines) and re.match(r"(\d+\.|-)\s+", lines[i + 1]):
                    pass
                else:
                    break
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"(#{1,4}\s|```|\||\d+\.\s|-\s)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)


TEMPLATE = """<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Cyanescent Player 1.0.0</title>
  <meta name="description" content="{title} for Cyanescent Player 1.0.0.">
  <meta name="theme-color" content="#06070d">
  <link rel="canonical" href="https://cyanescent-dev.github.io/docs/{file}">
  <link rel="icon" type="image/png" sizes="64x64" href="../assets/v1/icon-64.png">
  <link rel="apple-touch-icon" href="../assets/v1/icon-180.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../v1.css">
</head>
<body>
  <a href="#main" class="skip-link">Skip to content</a>
  <header class="nav">
    <nav class="wrap nav-inner" aria-label="Primary">
      <a href="../" class="brand"><img src="../assets/v1/icon-64.png" alt="" width="30" height="30">Cyanescent</a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-links">
        <span class="visually-hidden">Menu</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
      </button>
      <ul id="nav-links" class="nav-links">
        <li><a href="../#editions">Editions</a></li>
        <li><a href="../#licence">Licence</a></li>
        <li><a href="../support.html">Support</a></li>
        <li><a href="../psy-roller/">Psy-Roller</a></li>
        <li><a href="../#download" class="btn btn-primary btn-sm">Download Free</a></li>
      </ul>
    </nav>
  </header>
  <main id="main" class="doc">
    <div class="wrap doc-inner">
      <nav aria-label="Documentation">
        <ul class="doc-nav">
{docnav}
        </ul>
      </nav>
      <p class="doc-meta">Cyanescent Player 1.0.0 · This page reproduces the document supplied with the release downloads.</p>
{body}
    </div>
  </main>
  <footer class="footer">
    <div class="wrap footer-grid">
      <p>Cyanescent Player 1.0.0 · © 2026 Samuel Ferguson. All rights reserved.</p>
      <nav aria-label="Footer">
        <ul>
          <li><a href="quick-start.html">Quick Start</a></li>
          <li><a href="licence.html">Licence (EULA)</a></li>
          <li><a href="third-party-notices.html">Third-party notices</a></li>
          <li><a href="hd-worlds.html">HD World installation</a></li>
          <li><a href="../support.html">Support</a></li>
          <li><a href="../privacy.html">Privacy</a></li>
        </ul>
      </nav>
    </div>
  </footer>
  <script src="../v1.js"></script>
</body>
</html>
"""


def main():
    verify_sources()
    for file, _label, title, sources in PAGES:
        current = ' aria-current="page"'
        docnav = "\n".join(
            f'          <li><a href="{f}"{current if f == file else ""}>{label}</a></li>'
            for f, label, _t, _s in PAGES
        )
        body = "\n".join(render((SOURCE / s).read_text(encoding="utf-8")) for s in sources)
        body = PREFACE.get(file, "") + body
        page = TEMPLATE.format(title=html.escape(title), file=file, docnav=docnav, body=body)
        (OUT / file).write_text(page, encoding="utf-8")
        print(f"wrote docs/{file}")


if __name__ == "__main__":
    main()
