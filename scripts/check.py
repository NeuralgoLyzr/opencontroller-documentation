#!/usr/bin/env python3
"""The site's structural checks, run in CI and by hand from the site's root.

Every page in docs.json exists; every page is listed in docs.json; every
page has a title and a description; every internal link points at a page.
"""
import glob
import json
import os
import re
import sys

problems = []
pages = {os.path.splitext(f)[0] for f in glob.glob("**/*.mdx", recursive=True)}

nav = json.load(open("docs.json"))
listed = set()


def walk(items):
    for p in items:
        if isinstance(p, str):
            listed.add(p)
        elif isinstance(p, dict) and "pages" in p:
            walk(p["pages"])


for tab in nav["navigation"]["tabs"]:
    for group in tab["groups"]:
        walk(group.get("pages", []))

for p in sorted(listed - pages):
    problems.append(f"docs.json lists {p}, which does not exist")
# Pages a flag has turned off (flags.json, scripts/flags.py) are meant to be out of the navigation.
flags = json.load(open("flags.json"))
off = () if flags.get("apiReference") else ("api-reference/",)
for p in sorted(pages - listed):
    if not p.startswith("snippets/") and not p.startswith(off):
        problems.append(f"{p}.mdx is not in docs.json")

for f in sorted(glob.glob("**/*.mdx", recursive=True)):
    s = open(f).read()
    if f.startswith("snippets/"):
        continue
    if not s.startswith("---"):
        problems.append(f"{f}: no frontmatter")
    else:
        head = s.split("---", 2)[1]
        for key in ("title", "description"):
            if not re.search(rf"^{key}:", head, re.M):
                problems.append(f"{f}: no {key}")
    for m in re.finditer(r'href="(/[^"#]+)|\]\((/[^)#]+)\)', s):
        link = (m.group(1) or m.group(2)).rstrip("/").lstrip("/")
        if link.startswith("images/"):
            if not os.path.exists(link):
                problems.append(f"{f}: missing image {link}")
        elif link not in pages:
            problems.append(f"{f}: broken link /{link}")

for p in problems:
    print(p)
print(f"{len(pages)} pages, {len(problems)} problems")
sys.exit(1 if problems else 0)
