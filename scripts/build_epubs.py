#!/usr/bin/env python3
"""Build reflowable EPUB editions of every drafted chapter into epub/.

EPUB is the format for e-readers (Send to Kindle, Apple Books, Kobo):
the print PDFs in pdf/ are fixed-layout pages, which Kindle's document
pipeline renders poorly or rejects as an invalid item. This script
strips the screen-only furniture from each chapter and hands the clean
HTML to pandoc, using the chapter frontispiece as the cover.

Requires pandoc (https://pandoc.org). Run from anywhere:
    python3 scripts/build_epubs.py
Regenerate whenever a chapter HTML changes.
"""
import os
import re
import subprocess
import sys

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

SERIES = "The Human Mind & the Architecture of Belief"

CHAPTERS = {  # chapter html -> output stem (matches pdf/ naming)
    "v1-ch01-predicting-brain.html": "V1-Ch01-The-World-You-Cannot-Reach",
    "v1-ch02-two-minds.html": "V1-Ch02-Two-Minds-in-One-Head",
    "v1-ch03-catalogue.html": "V1-Ch03-The-Catalogue-of-Beautiful-Mistakes",
    "v1-ch04-memory.html": "V1-Ch04-The-Story-We-Rewrite-Each-Night",
    "v1-ch05-attention.html": "V1-Ch05-The-Spotlight-and-the-Dark",
    "v1-ch06-how-we-decide.html": "V1-Ch06-How-We-Decide",
    "v1-ch07-automatic-self.html": "V1-Ch07-The-Automatic-Self",
    "v1-ch08-cleverness.html": "V1-Ch08-Cleverness-and-Its-Myths",
    "v7-ch01-why-we-see.html": "V7-Ch01-Why-We-See-What-Isnt-There",
    "v7-ch02-possessed.html": "V7-Ch02-The-Possessed",
    "v7-ch03-ghost-in-the-plate.html": "V7-Ch03-The-Ghost-in-the-Plate",
    "v7-ch05-witches.html": "V7-Ch05-Witches-and-the-Black-Art",
    "v7-ch06-stars-and-hand.html": "V7-Ch06-The-Stars-and-the-Hand",
    "v7-ch07-pseudoscience-museum.html": "V7-Ch07-The-Pseudoscience-Museum",
    "v7-ch08-god-and-mystic-brain.html": "V7-Ch08-God-and-the-Mystic-Brain",
    "v7-ch09-conspiratorial-mind.html": "V7-Ch09-The-Conspiratorial-Mind",
    "v7-ch10-honest-investigation.html": "V7-Ch10-The-Honest-Investigation",
}

EPUB_CSS = """\
body { font-family: Georgia, 'Times New Roman', serif; line-height: 1.5; }
h1, h2, h3, h4 { font-family: Georgia, serif; line-height: 1.2; }
h2, h3 { text-align: center; }
img { max-width: 100%; height: auto; }
figure { margin: 1em 0; text-align: center; page-break-inside: avoid; }
figcaption { font-size: 0.85em; font-style: italic; }
.kicker, .aside-label, .tier-label, .rt-kicker { font-variant: small-caps; letter-spacing: 0.08em; }
.credit, .cite, .gloss { font-size: 0.85em; }
.epigraph, .pull, .scene { font-style: italic; text-align: center; }
.tier, .box, .consult, .roundtable, .mvr, .essence { margin: 1em 0; padding: 0.6em 0.9em; border: 1px solid #999; }
.tagref { font-size: 0.75em; border: 1px solid #999; padding: 0 0.3em; margin-right: 0.4em; }
"""

os.makedirs("epub", exist_ok=True)
css_path = "epub/_epub.css"
with open(css_path, "w", encoding="utf-8") as fh:
    fh.write(EPUB_CSS)

failures = []
for src, stem in CHAPTERS.items():
    html = open(f"chapters/{src}", encoding="utf-8").read()
    title = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
    title = re.sub(r"\s+", " ", title)
    # strip screen furniture: running head/foot, chapter nav, scripts, head links
    for pat in (
        r'<div class="runhead">.*?</div>\s*',
        r'<div class="runfoot">.*?</div>\s*',
        r'<nav class="ch-nav">.*?</nav>\s*',
        r"<script\b[^>]*>.*?</script>\s*|<script\b[^>]*/>\s*",
        r"<link\b[^>]*>\s*",
        r'<meta property="og:[^"]*"[^>]*>\s*',
    ):
        html = re.sub(pat, "", html, flags=re.S)
    cover = re.search(r'<img[^>]*src="\.\./([^"]+)"', html).group(1)
    tmp = f"chapters/_epub_{src}"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(html)
    out = f"epub/{stem}.epub"
    cmd = [
        "pandoc", tmp, "-f", "html", "-t", "epub3", "-o", out,
        # chapter img paths are ../assets/...; pandoc resolves resources
        # against the working directory, so search from chapters/ too
        "--resource-path", ".:chapters",
        "--metadata", f"title={title}",
        "--metadata", f"author={SERIES}",
        "--metadata", "lang=en",
        "--epub-cover-image", cover,
        "--css", css_path,
        "--split-level=1",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    os.remove(tmp)
    if r.returncode != 0 or not os.path.getsize(out):
        failures.append((src, r.stderr.strip()[:300]))
        print(f"FAIL {out}\n     {r.stderr.strip()[:300]}")
    else:
        print(f"OK   {out}  ({os.path.getsize(out)//1024} KB)")

if failures:
    sys.exit(1)
print(f"\n{len(CHAPTERS)} EPUBs built into epub/")
