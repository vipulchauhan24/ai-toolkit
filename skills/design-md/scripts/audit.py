#!/usr/bin/env python3
"""Static checks on built CSS and HTML. Standard library only.

Usage:

    python3 -I audit.py FILE_OR_FOLDER [...]

Checks raw colours outside the token files, `transition: all`, animating layout properties,
removing focus outlines, inline styles, images with no alt, width or height, and parallax
that breaks its limits.
A line ending in `/* audit:ok <reason> */` is skipped.
Output lines start with FAIL or RESULT. Exit codes: 0 pass, 1 a FAIL, 2 usage error.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

TOKEN_FILES = {"tokens.css", "design.css"}
RAW_COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|oklch|oklab|lab|lch)\(")
LAYOUT_ANIM = re.compile(r"transition(?:-property)?:[^;]*\b(?:width|height|top|left|right|bottom|margin[a-z-]*)\b")
OUTLINE_OFF = re.compile(r"outline:\s*(?:none|0)\b")
ANYWHERE_OK = "audit:ok"
TEXT_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "a", "button", "li", "blockquote"}


def strip_data_uris(line):
    return re.sub(r'url\((["\']?)data:.*?\1\)', "url()", line)


def check_css(path, text, fails):
    for n, line in enumerate(text.split("\n"), 1):
        if ANYWHERE_OK in line:
            continue
        clean = strip_data_uris(line)
        if path.name not in TOKEN_FILES and RAW_COLOUR.search(clean):
            fails.append("%s:%d: raw-colour: use a colour token: %s" % (path, n, line.strip()[:70]))
        if re.search(r"transition(?:-property)?:\s*all\b|transition:[^;]*\ball\s+\d", clean):
            fails.append("%s:%d: transition-all: name the properties" % (path, n))
        if LAYOUT_ANIM.search(clean):
            fails.append("%s:%d: layout-animation: animate transform and opacity" % (path, n))
        if OUTLINE_OFF.search(clean):
            fails.append("%s:%d: outline-removed: keep a visible focus style" % (path, n))


class Html(HTMLParser):
    def __init__(self, path, fails):
        super().__init__(convert_charrefs=True)
        self.path, self.fails = path, fails
        self.scroll_linked = 0
        self.frame = None  # [tag, depth of that tag, has media, line] while inside a parallax frame

    def handle_data(self, data):
        if self.frame and data.strip():
            self.fail_text()

    def fail_text(self):
        message = "%s:%d: parallax-text: a parallax frame holds images only, never text" % (self.path, self.frame[3])
        if message not in self.fails:
            self.fails.append(message)

    def handle_endtag(self, tag):
        if not self.frame or tag != self.frame[0]:
            return
        self.frame[1] -= 1
        if self.frame[1] == 0:
            if not self.frame[2]:
                self.fails.append("%s:%d: parallax-no-image: a parallax frame needs an img or video" % (self.path, self.frame[3]))
            self.frame = None

    def track_parallax(self, tag, a, where):
        if self.frame:
            if tag == self.frame[0]:
                self.frame[1] += 1
            self.frame[2] = self.frame[2] or tag in ("img", "video")
            if tag in TEXT_TAGS:
                self.fail_text()
        if "data-timeline" in a or "data-parallax" in a:
            self.scroll_linked += 1
            if self.scroll_linked == 2:
                self.fails.append("%s: scroll-linked: a page has at most one data-parallax or data-timeline" % where)
        if "data-parallax" in a:
            if tag in ("img", "video"):
                self.fails.append("%s: parallax-frame: put data-parallax on the frame around the image" % where)
            elif tag in TEXT_TAGS:
                self.fails.append("%s: parallax-text: a parallax frame holds images only, never text" % where)
            elif not self.frame:
                self.frame = [tag, 1, False, self.getpos()[0]]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        where = "%s:%d" % (self.path, self.getpos()[0])
        self.track_parallax(tag, a, where)
        style = a.get("style")
        if style and not all(p.strip().startswith("--_") for p in style.split(";") if p.strip()):
            self.fails.append("%s: inline-style: move this to CSS: %s" % (where, style[:50]))
        if tag == "img":
            if "alt" not in a:
                self.fails.append("%s: img-alt: image has no alt" % where)
            if "width" not in a or "height" not in a:
                self.fails.append("%s: img-size: image needs width and height" % where)


def files_in(items):
    for item in items:
        path = Path(item)
        if path.is_dir():
            yield from (f for f in sorted(path.rglob("*")) if f.suffix in (".css", ".html"))
        else:
            yield path


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args or not all(Path(a).exists() for a in args):
        print("usage: audit.py FILE_OR_FOLDER [...]", file=sys.stderr)
        return 2
    fails = []
    count = 0
    for path in files_in(args):
        text = path.read_text(encoding="utf-8")
        count += 1
        if path.suffix == ".css":
            check_css(path, text, fails)
        elif path.suffix == ".html":
            Html(path, fails).feed(text)
    for line in fails:
        print("FAIL " + line)
    print("OK   %d file(s) checked" % count)
    print("RESULT  %s" % ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
