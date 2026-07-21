#!/usr/bin/env python3
"""Link checker for the book repo.

Verifies, for every HTML page in the repo:
  1. every relative href/src resolves to a real file;
  2. every chapter's ch-nav prev/next target exists;
  3. every chapter is reachable from index.html or a volume contents page.

Run from the repo root:  python3 scripts/check_links.py
Exits non-zero on any failure, so it can gate a commit or CI job.
"""
import glob
import os
import re
import sys

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

HUBS = ["index.html", "volume-1.html", "volume-7.html"]
pages = HUBS + sorted(glob.glob("chapters/*.html"))
errors = []

# 1. every relative reference resolves
for page in pages:
    src = open(page, encoding="utf-8").read()
    base = os.path.dirname(page)
    for ref in re.findall(r'(?:href|src)="([^"#]+)"', src):
        if ref.startswith(("http://", "https://", "mailto:", "data:")):
            continue
        target = os.path.normpath(os.path.join(base, ref.split("?")[0]))
        if not os.path.exists(target):
            errors.append(f"{page}: broken reference -> {ref}")

# 2. ch-nav blocks point at real files
for page in sorted(glob.glob("chapters/*.html")):
    src = open(page, encoding="utf-8").read()
    navs = re.findall(r'<nav class="ch-nav">.*?</nav>', src, re.S)
    if len(navs) != 1:
        errors.append(f"{page}: expected exactly one ch-nav block, found {len(navs)}")
        continue
    for href in re.findall(r'href="([^"]+)"', navs[0]):
        target = os.path.normpath(os.path.join("chapters", href))
        if not os.path.exists(target):
            errors.append(f"{page}: ch-nav target missing -> {href}")

# 3. every chapter is linked from a hub
linked = set()
for hub in HUBS:
    src = open(hub, encoding="utf-8").read()
    linked |= set(re.findall(r'href="(chapters/[^"#]+)"', src))
for chapter in sorted(glob.glob("chapters/*.html")):
    if chapter not in linked:
        errors.append(f"{chapter}: orphan - not linked from any contents page")

if errors:
    print(f"FAIL: {len(errors)} problem(s)")
    for e in errors:
        print("  " + e)
    sys.exit(1)
print(f"OK: {len(pages)} pages, all references resolve, nav chains intact, no orphans")
