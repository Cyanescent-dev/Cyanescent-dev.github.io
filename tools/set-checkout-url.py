#!/usr/bin/env python3
"""Insert (or remove) the Lemon Squeezy checkout link on the Pro button.

  python3 tools/set-checkout-url.py https://cyanescent.lemonsqueezy.com/buy/<uuid>          # live
  python3 tools/set-checkout-url.py --test https://cyanescent.lemonsqueezy.com/buy/<uuid>   # local testing only
  python3 tools/set-checkout-url.py --reset                                                 # back to gated

Only edits the #pro-checkout button and its note in index.html. A --test link is
marked data-checkout="test"; tools/check-site.py --launch refuses to pass while it
is present, so a test checkout cannot be deployed by accident.
"""

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

INDEX = Path(__file__).resolve().parent.parent / "index.html"
HOST = "cyanescent.lemonsqueezy.com"
PATH = re.compile(r"^/(checkout/)?buy/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/?$")

BUTTON = re.compile(r'<a id="pro-checkout"[^>]*>Get Pro — \$5</a>')
NOTE = re.compile(r'\n\s*<span id="pro-checkout-note"[^>]*>.*?</span>')
GATED = ('<a id="pro-checkout" class="btn btn-pro" role="link" aria-disabled="true" '
         'data-launch-pending="pro-checkout">Get Pro — $5</a>')
GATED_NOTE = ('\n            <span id="pro-checkout-note" class="pending-note" '
              'data-launch-pending="pro-checkout-note">Preview: checkout opens at launch.</span>')
TEST_NOTE = ('\n            <span id="pro-checkout-note" class="pending-note">'
             'Local test checkout. Never deploy this link.</span>')


def main(argv):
    test = "--test" in argv
    args = [a for a in argv if not a.startswith("--")]
    if "--reset" in argv:
        button, note = GATED, GATED_NOTE
    else:
        if len(args) != 1:
            sys.exit(__doc__)
        url = args[0].strip()
        u = urlparse(url)
        if u.scheme != "https" or u.netloc != HOST or not PATH.match(u.path):
            sys.exit(f"Refusing {url!r}: expected https://{HOST}/buy/<product-variant uuid>")
        if u.query or u.fragment:
            sys.exit("Refusing a URL with query parameters or fragments; use the plain hosted checkout link")
        mode = "test" if test else "live"
        button = f'<a id="pro-checkout" class="btn btn-pro" href="{url}" data-checkout="{mode}">Get Pro — $5</a>'
        note = TEST_NOTE if test else ""

    html = INDEX.read_text(encoding="utf-8")
    if len(BUTTON.findall(html)) != 1:
        sys.exit("Could not find exactly one #pro-checkout button in index.html")
    html = BUTTON.sub(lambda _m: button, html)
    html = NOTE.sub("", html)
    html = html.replace(button, button + note, 1)
    INDEX.write_text(html, encoding="utf-8")
    print("Pro checkout:", "gated" if "--reset" in argv else f"{'TEST (local only)' if test else 'LIVE'} {args[0]}")


if __name__ == "__main__":
    main(sys.argv[1:])
