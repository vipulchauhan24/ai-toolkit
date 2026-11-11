#!/usr/bin/env python3
"""Checks page copy before any markup is written, and built HTML pages after. Standard library only.

Usage:

    python3 -I check_copy.py COPY.md
    python3 -I check_copy.py --facts COPY.md dist/index.html dist/about.html
    python3 -I check_copy.py --allow harness,bespoke COPY.md

A .md file must follow the format in references/copy/copy.md. An .html file is read for
its visible text; without --facts its numbers and quotes are not traced.

Output lines start with OK, WARN, FAIL or RESULT. WARN does not fail the run.
Exit codes: 0 pass, 1 a FAIL, 2 usage error.
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

KINDS = {"portfolio", "saas", "app", "blog", "service", "ecommerce", "place", "event"}
PLAIN_READERS = {"service", "ecommerce", "place", "event"}  # general public: grade 9. The others: grade 12.
ROLES = {"title", "description", "eyebrow", "h1", "h2", "h3", "sub", "body", "item", "stat", "button", "link", "label",
         "hint", "error", "success", "empty", "loading", "quote", "alt", "meta"}
TEXT_ROLES = {"sub", "body", "item", "quote"}
HEADINGS = {"h1", "h2", "h3"}

AI_WORDS = re.compile(r"\b(?:delve[sd]?|delving|tapestry|testament|pivotal|underscores?|underscoring|showcas(?:e|es|ed|ing)|realm|embark(?:s|ing)?|"
                      r"beacon|multifaceted|myriad|plethora|meticulous(?:ly)?|intricate|interplay|garner(?:s|ed)?|leverag(?:e|es|ed|ing)|utili[sz](?:e|es|ed|ing)|"
                      r"elevat(?:e|es|ing)|unlock(?:s|ing)?|unleash(?:es|ing)?|empower(?:s|ing)?|harness(?:es|ing)?|supercharg(?:e|es|ing)|turbocharg(?:e|es|ing)|"
                      r"seamless(?:ly)?|effortless(?:ly)?|cutting-edge|revolutionary|transformative|holistic|next-level|next-generation|world-class|"
                      r"best-in-class|game-chang(?:er|ing)|state-of-the-art|synerg(?:y|ies)|reimagin(?:e|ed|ing)|robust|nestled|vibrant|groundbreaking|"
                      r"unparalleled|streamlin(?:e|es|ed|ing)|foster(?:s|ing)?|crucial|comprehensive|innovative|passionate)\b", re.I)
STOCK = re.compile(r"in today'?s (?:fast-paced|digital|modern)|unlock the power|take (?:\w+ ){1,3}to the next level|look no further|at your fingertips|"
                   r"say goodbye to|whether you'?re|the future of \w+ is|where \w+ meets \w+|built for the modern|imagine a world|ready to transform|"
                   r"join thousands|trusted by teams worldwide|one-stop shop|made simple\b|results-driven|detail-oriented|team player|proven track record|"
                   r"in the heart of|in summary\b|in conclusion\b|let that sink in|here'?s the thing", re.I)
RESIDUE = re.compile(r"lorem ipsum|\{\{|\}\}|\[(?:need|your|company|name|insert|todo|placeholder)\b|\bTODO\b|\bTBD\b|\*\*|^#+ |as an ai\b|i hope this helps|"
                     r"^certainly[!,]|would you like me|your (?:name|text) here|placeholder text", re.I)
COMING_SOON = re.compile(r"coming soon", re.I)
CONTRAST = re.compile(r"\bnot (?:just|only|merely)\b|\b(?:it|this|that)(?:'|’)?s not\b|\bisn(?:'|’)t (?:just|only|a|an|about)\b|\brather than\b|\binstead of\b|\bwithout the\b|\bmore than (?:just )?an?\b|\bNo \w+[.,] No \w+", re.I)
PUFFERY = re.compile(r"\bserves? as\b|\bstands? as\b|\bboasts?\b|\bplays? an? (?:key|vital|crucial|pivotal|important) role\b|\bis a reminder\b|\bspeaks? volumes\b", re.I)
ING_RIDER = re.compile(r",\s+(?:ensuring|highlighting|showcasing|fostering|enabling|allowing|providing|helping|empowering|underscoring|reflecting|delivering|driving)\b", re.I)
VIRTUE = re.compile(r"\b(?:honest(?:ly)?|genuine(?:ly)?|truly|simply|actually|thoughtful(?:ly)?|intentional(?:ly)?|carefully|dependable)\b", re.I)
TRANSITION = re.compile(r"(?:^|[.!?]\s+)(?:additionally|furthermore|moreover|notably|consequently)\b", re.I)
PROCESS = re.compile(r"\bthis section\b|\bbelow,? you(?:'|’)ll find\b|\bhere are \d|\bwe(?:'|’)ve added\b|\bon this page\b", re.I)
TRIPLE = re.compile(r"\b[\w-]+, [\w-]+,? and [\w-]+\b")
STOCK_NAME = re.compile(r"\b(?:Sarah Chen|Alex Rivera|Priya|Okafor|Elara|Marcus Webb|Jane Doe|John Doe|Acme|Northwind|Lumen|Halcyon|Kestrel|Nimbus)\b")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
EM_DASH = "—"
VAGUE_FAIL = {"click here", "click", "submit", "here"}
VAGUE_WARN = {"learn more", "read more", "get started", "more", "explore", "discover", "see more", "go"}
ALT_FILLER = re.compile(r"^(?:an? )?(?:image|picture|photo|graphic) of\b", re.I)
NUMBER = re.compile(r"(?<![A-Za-z0-9.,])\d[\d,]*(?:\.\d+)?(?=x\b|[^A-Za-z0-9]|$)")
BUDGETS = {  # id: (allowed per page, fail above this, or None if it only warns)
    "contrast": (2, 4), "puffery": (0, 2), "ing-rider": (1, 3), "virtue": (2, None), "transition": (1, None), "triple": (2, None),
    "exclamation": (0, 2), "two-fragment": (1, 2), "em-dash": (3, None), "ai-word": (0, 2),
}


class Report:
    def __init__(self, path):
        self.path = path
        self.fails = 0
        self.warns = 0

    def fail(self, line, cid, message):
        self.fails += 1
        print("FAIL %s:%d: %s: %s" % (self.path, line, cid, message))

    def warn(self, line, cid, message):
        self.warns += 1
        print("WARN %s:%d: %s: %s" % (self.path, line, cid, message))


class Page:
    def __init__(self, name, line):
        self.name = name
        self.line = line
        self.items = []  # (role, text, line, section)

    def add(self, role, text, line, section):
        self.items.append((role, text, line, section))

    def of(self, *roles):
        return [i for i in self.items if i[0] in roles]


class Document:
    def __init__(self):
        self.kind = None
        self.pages = []
        self.facts = ""
        self.has_facts = False
        self.allow = set()
        self.gaps = 0


def parse_copy(text, report):
    doc = Document()
    page = None
    section = None
    facts = []
    for n, raw in enumerate(text.split("\n"), 1):
        line = raw.strip()
        if not line or line.startswith("<!--"):
            continue
        low = line.lower()
        m = re.match(r"^# page:\s*(.+)$", line, re.I)
        if m:
            page = Page(m.group(1).strip(), n)
            doc.pages.append(page)
            section = None
            continue
        m = re.match(r"^##\s+(.+)$", line)
        if m:
            section = m.group(1).strip().lower()
            if section == "facts":
                doc.has_facts = True
            continue
        if section == "facts":
            facts.append(line)
            continue
        if section == "missing":
            doc.gaps += 1
            continue
        m = re.match(r"^([a-z0-9]+):\s*(.*)$", line)
        if page is None:
            if low.startswith("kind:"):
                doc.kind = line.split(":", 1)[1].strip().lower()
            elif low.startswith("allow:"):
                doc.allow |= {w.strip().lower() for w in line.split(":", 1)[1].split(",") if w.strip()}
            elif low.startswith("voice:"):
                pass
            else:
                report.fail(n, "format", "before the first page only kind:, voice:, allow: and ## facts are allowed: %s" % line[:60])
            continue
        if not m or m.group(1) not in ROLES:
            report.fail(n, "format", "each line needs a known role, such as h2: or body: %s" % line[:60])
            continue
        if not m.group(2).strip():
            report.fail(n, "format", "%s: has no text" % m.group(1))
            continue
        page.add(m.group(1), m.group(2).strip(), n, section)
    doc.facts = "\n".join(facts)
    if doc.kind not in KINDS:
        report.fail(1, "format", "kind: must be one of %s" % ", ".join(sorted(KINDS)))
    if not doc.has_facts:
        report.fail(1, "format", "the file has no ## facts section")
    if not doc.pages:
        report.fail(1, "format", "the file has no # page: heading")
    return doc


class Html(HTMLParser):
    MAP = {"h1": "h1", "h2": "h2", "h3": "h3", "p": "body", "li": "item", "button": "button", "a": "link", "label": "label", "blockquote": "quote", "title": "title"}
    SKIP = {"script", "style", "noscript", "template", "svg"}

    def __init__(self, page):
        super().__init__(convert_charrefs=True)
        self.page = page
        self.stack = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and (a.get("name") or "").lower() == "description" and a.get("content"):
            self.page.add("description", a["content"].strip(), self.getpos()[0], None)
        if tag == "img" and a.get("alt"):
            self.page.add("alt", a["alt"].strip(), self.getpos()[0], None)
        if tag in self.SKIP:
            self.skip += 1
        elif tag in self.MAP:
            self.stack.append([self.MAP[tag], "", self.getpos()[0]])

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag in self.MAP and self.stack:
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == self.MAP[tag]:
                    role, text, line = self.stack.pop(i)
                    text = re.sub(r"\s+", " ", text).strip()
                    if text:
                        self.page.add(role, text, line, None)
                    break

    def handle_data(self, data):
        if not self.skip and self.stack:
            self.stack[-1][1] += data


def parse_html(text, path):
    doc = Document()
    page = Page(path.name, 1)
    doc.pages.append(page)
    parser = Html(page)
    parser.feed(text)
    return doc


def budget(report, cid, hits, message):
    """hits is a list of (line, sample). Over the allowance warns; far over fails."""
    allowed, fail_above = BUDGETS[cid]
    if len(hits) <= allowed:
        return
    line, sample = hits[allowed]
    note = "%d on this page (allowed %d): %s. %s" % (len(hits), allowed, sample[:50], message)
    if fail_above is not None and len(hits) > fail_above:
        report.fail(line, cid, note)
    else:
        report.warn(line, cid, note)


def count(pattern, items):
    return [(i[2], m.group(0)) for i in items for m in pattern.finditer(i[1])]


def syllables(word):
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    n = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and not word.endswith("le") and n > 1:
        n -= 1
    return max(n, 1)


def reading_grade(text):
    sentences = max(1, len(re.findall(r"[.!?]+(?:\s|$)", text)))
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
    if not words:
        return 0.0, 0
    return 0.39 * len(words) / sentences + 11.8 * sum(syllables(w) for w in words) / len(words) - 15.59, len(words)


def sentences_of(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def check_page(page, doc, report, is_copy, trace):
    items = page.items
    prose = [i for i in items if i[0] not in ("meta", "alt", "title", "description")]

    for i in prose:
        role, text, line, _ = i
        if RESIDUE.search(text) or (is_copy and re.search(r"\[[^\]]+\]", text)):
            report.fail(line, "residue", "template or chatbot text left in: %s" % text[:60])
        if COMING_SOON.search(text) and doc.kind != "event":
            report.fail(line, "residue", "\"Coming soon\" on a finished page: drop the section and list what is missing")
        m = STOCK.search(text)
        if m:
            report.fail(line, "stock-phrase", "stock line: %s" % m.group(0))
        m = STOCK_NAME.search(text)
        if m:
            report.warn(line, "stock-name", "a name models reach for: %s. Use only names from the fact sheet" % m.group(0))
        if (role in HEADINGS or role in ("item", "button")) and EMOJI.search(text):
            report.fail(line, "emoji", "emoji in a %s" % role)

    words = [(n, s) for n, s in count(AI_WORDS, prose) if s.lower() not in doc.allow]
    budget(report, "ai-word", words, "Replace each with the fact it stands in for")
    budget(report, "contrast", count(CONTRAST, prose), "State the positive fact alone")
    budget(report, "puffery", count(PUFFERY, prose), "Use is or has")
    budget(report, "ing-rider", count(ING_RIDER, prose), "End the sentence at the fact")
    budget(report, "virtue", count(VIRTUE, prose), "Show it with a fact")
    budget(report, "transition", count(TRANSITION, prose), "Start with the point")
    budget(report, "triple", count(TRIPLE, prose), "List as many as there are")
    budget(report, "exclamation", [(i[2], i[1]) for i in prose for _ in re.findall("!", i[1])], "Remove them")
    budget(report, "em-dash", [(i[2], i[1]) for i in prose for _ in re.findall(EM_DASH, i[1])], "Use a full stop, colon or comma")
    for line, sample in count(PROCESS, prose):
        report.warn(line, "process-talk", "the page talks about itself: %s" % sample)

    # Headings
    h1s = page.of("h1")
    if len(h1s) != 1:
        report.fail(h1s[1][2] if len(h1s) > 1 else page.line, "h1", "a page needs exactly one h1, found %d" % len(h1s))
    for role, text, line, _ in h1s:
        if len(text) > 80:
            report.fail(line, "h1-length", "%d characters: move detail to the supporting line" % len(text))
        elif len(text) > 60:
            report.warn(line, "h1-length", "%d characters: over two lines at display size" % len(text))
        if text.endswith("?"):
            report.warn(line, "h1-question", "a question the reader did not ask")
    fragments = []
    for role, text, line, _ in page.of(*HEADINGS):
        if re.fullmatch(r"[\w'’-]+\.\s+[\w'’-]+\.\s+[\w'’-]+\.", text):
            report.fail(line, "tricolon", "three one-word fragments: %s" % text)
        elif re.fullmatch(r"[^.]+\.\s+[^.]+\.", text):
            fragments.append((line, text))
        words_in = text.split()
        long_words = [w for w in words_in if len(w) > 3]
        if len(words_in) >= 3 and len(long_words) >= 2 and all(w[0].isupper() for w in long_words):
            report.warn(line, "title-case", "use sentence case: %s" % text[:50])
        if role != "h1" and len(text) > 60:
            report.warn(line, "heading-length", "%d characters" % len(text))
    budget(report, "two-fragment", fragments, "Name the thing in one phrase")

    # Buttons
    for role, text, line, _ in page.of("button"):
        low = text.lower().rstrip(" →")
        if low in VAGUE_FAIL:
            report.fail(line, "button", "says nothing about what happens: %s" % text)
        elif low in VAGUE_WARN:
            report.warn(line, "button", "name the action and the thing: %s" % text)
        elif len(text.split()) > 5:
            report.warn(line, "button", "over five words: %s" % text)
    hero_actions = [i for i in page.of("button") if i[3] == "hero"]
    if len(hero_actions) > 2:
        report.warn(hero_actions[2][2], "hero-actions", "%d buttons in the hero: at most two" % len(hero_actions))

    # Length and rhythm
    lengths = []
    for role, text, line, _ in page.of(*TEXT_ROLES):
        if len(text.split()) > 80:
            report.warn(line, "long-paragraph", "%d words: one idea per paragraph" % len(text.split()))
        for s in sentences_of(text):
            n = len(s.split())
            lengths.append(n)
            if n > 35:
                report.warn(line, "long-sentence", "%d words: %s" % (n, s[:50]))
    if len(lengths) >= 8:
        mean = sum(lengths) / len(lengths)
        spread = (sum((x - mean) ** 2 for x in lengths) / len(lengths)) ** 0.5
        if spread < 3:
            report.warn(page.line, "even-rhythm", "every sentence is about %d words long: vary them" % round(mean))
    body = " ".join(i[1] for i in page.of("sub", "body") + page.of("item"))
    grade, n_words = reading_grade(body)
    target = 9 if doc.kind in PLAIN_READERS else 12
    if n_words >= 60 and grade > target + 1:
        report.warn(page.line, "reading-level", "reads at about grade %.0f; aim for %d or below" % (grade, target))

    # Metadata and small text
    if is_copy:
        for role, limit in (("title", 60), ("description", 160)):
            found = page.of(role)
            if not found:
                report.fail(page.line, "meta-missing", "page %s has no %s:" % (page.name, role))
            elif len(found[0][1]) > limit:
                report.warn(found[0][2], "meta-length", "%s is %d characters; search results cut it at about %d" % (role, len(found[0][1]), limit))
    for role, text, line, _ in page.of("alt"):
        if ALT_FILLER.search(text):
            report.warn(line, "alt", "describe the content, not the fact that it is a picture: %s" % text[:40])

    # Forms need their states
    if is_copy and page.of("label") and not (page.of("error") and page.of("success")):
        report.fail(page.of("label")[0][2], "form-states", "a form needs at least one error: line and one success: line")

    # Facts: every number and quote traces back to the fact sheet
    if trace:
        known = {n.rstrip(",").replace(",", "") for n in NUMBER.findall(doc.facts)}
        for i in prose:
            if i[0] == "quote":
                continue
            for n in NUMBER.findall(i[1]):
                if n.rstrip(",").replace(",", "") not in known:
                    report.fail(i[2], "unsourced-number", "%s is not in the fact sheet: %s" % (n.rstrip(","), i[1][:50]))
        flat = re.sub(r"[\"“”'‘’]", "", doc.facts).lower()
        for role, text, line, _ in page.of("quote"):
            if re.sub(r"[\"“”'‘’]", "", text).lower() not in flat:
                report.fail(line, "unsourced-quote", "this quote is not in the fact sheet, word for word: %s" % text[:50])


def straight_marks(doc, report):
    """Reported once per file, because a draft usually has them throughout."""
    for page in doc.pages:
        for i in page.items:
            if i[0] != "meta" and (re.search(r"\w'\w|\"|\.\.\.", i[1])):
                report.warn(i[2], "typography", "use curly quotes and a real ellipsis: %s" % i[1][:40])
                return


def run_file(path, args, shown):
    report = Report(shown)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        report.fail(1, "format", "cannot be read: %s" % exc)
        return report
    is_copy = path.suffix.lower() in (".md", ".markdown")
    doc = parse_copy(text, report) if is_copy else parse_html(text, path)
    doc.allow |= args.allow
    trace = is_copy
    if not is_copy and args.facts:
        sheet = parse_copy(Path(args.facts).read_text(encoding="utf-8"), Report(args.facts))
        doc.facts, doc.kind, trace = sheet.facts, sheet.kind, True
        doc.allow |= sheet.allow
    for page in doc.pages:
        check_page(page, doc, report, is_copy, trace)
    if is_copy and doc.kind == "app":
        everything = [i for p in doc.pages for i in p.items]
        for role in ("empty", "error"):
            if not any(i[0] == role for i in everything):
                report.fail(1, "missing-state", "app screens need at least one %s: line" % role)
    straight_marks(doc, report)
    print("OK   %s: %d page(s), %d gap(s) listed, %d fail, %d warn" % (shown, len(doc.pages), doc.gaps, report.fails, report.warns))
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description="Copy checks for the ui-craft skill.")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--facts", default=None, help="a COPY.md whose fact sheet the HTML's numbers and quotes must trace to")
    ap.add_argument("--allow", default="", help="comma-separated words that are literal for this client")
    args = ap.parse_args(argv)
    if not args.files:
        print("usage: check_copy.py [--facts COPY.md] [--allow a,b] FILE [FILE ...]", file=sys.stderr)
        return 2
    args.allow = {w.strip().lower() for w in args.allow.split(",") if w.strip()}
    if args.facts and not Path(args.facts).is_file():
        print("usage error: %s is not a file" % args.facts, file=sys.stderr)
        return 2
    failed = 0
    for name in args.files:
        path = Path(name)
        if not path.is_file():
            print("usage error: %s is not a file" % name, file=sys.stderr)
            return 2
        failed += run_file(path, args, name).fails
    print("RESULT  %s" % ("FAIL" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
