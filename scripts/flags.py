#!/usr/bin/env python3
"""Applies flags.json to docs.json and the pages, or checks that it already has been.

A flag turns a part of the site on or off. Off, the part is out of the
navigation and its pages carry hidden: true, so they are neither listed,
searched nor in the sitemap, though the files stay in the repository and
a page still answers at its URL. Run from the site's root:

    python3 scripts/flags.py          # rewrite docs.json and the pages from flags.json
    python3 scripts/flags.py --check  # exit 1 if they disagree (CI)

Flags:
    apiReference   the API reference tab (api-reference/, and the OpenAPI endpoints)
    fineTuning     the Fine-tuning page, in an Improve group before Ask Ctrl (improve/)

The apiReference flag also writes snippets/api-link.mdx, the <ApiLink /> pages close
with: a line pointing at the API reference while it is on, nothing while it is off.
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
IMPROVE = {"group": "Improve", "pages": ["improve/fine-tuning"]}

# Each flag: the directory its pages live in.
PREFIX = {"apiReference": "api-reference/", "fineTuning": "improve/"}


def apply(docs, flags):
    tabs = [t for t in docs["navigation"]["tabs"] if t["tab"] != API_TAB["tab"]]
    if flags.get("apiReference"):
        tabs.append(API_TAB)
    docs["navigation"]["tabs"] = tabs
    groups = [g for g in tabs[0]["groups"] if g["group"] != IMPROVE["group"]]
    if flags.get("fineTuning"):
        at = next((i for i, g in enumerate(groups) if g["group"] == "Ask Ctrl"), len(groups))
        groups.insert(at, IMPROVE)
    tabs[0]["groups"] = groups
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


def api_link(on):
    if on:
        return ("{/* Written by scripts/flags.py from flags.json. Do not edit by hand. */}\n\n"
                'export const ApiLink = () => <p>The <a href="/api-reference/overview">API reference</a> lists the endpoints behind this page.</p>;\n')
    return ("{/* Written by scripts/flags.py from flags.json. Do not edit by hand. */}\n\n"
            "export const ApiLink = () => null;\n")


def off(flags):
    """The page prefixes the flags turn off, for scripts/check.py."""
    return tuple(p for f, p in PREFIX.items() if not flags.get(f))


def main():
    flags = json.load(open("flags.json"))
    docs = json.load(open("docs.json"))
    wanted = apply(json.loads(json.dumps(docs)), flags)
    check = "--check" in sys.argv
    stale = []
    for flag, prefix in PREFIX.items():
        stale += hide(prefix, not flags.get(flag), write=not check)
    link = api_link(bool(flags.get("apiReference")))
    try:
        current = open("snippets/api-link.mdx").read()
    except FileNotFoundError:
        current = None
    if current != link:
        stale.append("snippets/api-link.mdx")
        if not check:
            with open("snippets/api-link.mdx", "w") as f:
                f.write(link)
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
