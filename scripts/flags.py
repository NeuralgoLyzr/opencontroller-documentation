#!/usr/bin/env python3
"""Applies flags.json to docs.json, or checks that it already has been.

A flag turns a part of the site on or off. Off, the part is out of the
navigation and its pages carry hidden: true, so they are neither listed,
searched nor in the sitemap, though the files stay in the repository and
a page still answers at its URL. Run from the site's root:

    python3 scripts/flags.py          # rewrite docs.json from flags.json
    python3 scripts/flags.py --check  # exit 1 if docs.json disagrees (CI)

Flags:
    apiReference   the API reference tab (api-reference/, and the OpenAPI endpoints)
"""
import glob
import json
import re
import sys

API_TAB = {
    "tab": "API reference",
    "groups": [
        {"group": "Using the API", "pages": ["api-reference/overview", "api-reference/examples"]},
        {"group": "Endpoints", "openapi": "api-reference/openapi.json"},
    ],
}


def apply(docs, flags):
    tabs = [t for t in docs["navigation"]["tabs"] if t["tab"] != API_TAB["tab"]]
    if flags.get("apiReference"):
        tabs.append(API_TAB)
    docs["navigation"]["tabs"] = tabs
    return docs


# Marks every page under a prefix hidden, or unmarks it, in its frontmatter.
def hide(prefix, hidden, write):
    changed = []
    for path in sorted(glob.glob(f"{prefix}**/*.mdx", recursive=True)):
        s = open(path).read()
        head, body = s.split("\n---\n", 1)
        new = re.sub(r"\nhidden: true", "", head)
        if hidden:
            new += "\nhidden: true"
        if new != head:
            changed.append(path)
            if write:
                open(path, "w").write(new + "\n---\n" + body)
    return changed


def main():
    flags = json.load(open("flags.json"))
    docs = json.load(open("docs.json"))
    wanted = apply(json.loads(json.dumps(docs)), flags)
    check = "--check" in sys.argv
    stale = hide("api-reference/", not flags.get("apiReference"), write=not check)
    if check:
        if wanted != docs or stale:
            print("docs.json or the pages do not match flags.json: run python3 scripts/flags.py", file=sys.stderr)
            sys.exit(1)
        print("flags: docs.json matches flags.json")
        return
    with open("docs.json", "w") as f:
        json.dump(wanted, f, indent=2)
        f.write("\n")
    print("flags: " + ", ".join(f"{k}={'on' if v else 'off'}" for k, v in flags.items()))


if __name__ == "__main__":
    main()
