#!/usr/bin/env python3
"""Builds the control framework atlas from the posture pages.

The mapping is never written by hand: every control and the policies that
answer it come from posture/frameworks.mdx, and every policy's title from the
catalog on posture/security-policies.mdx. A policy's category is its prefix,
as the console's Findings page groups them. Run from the site's root:

    python3 scripts/atlas.py          # write snippets/atlas.mdx and atlas.js
    python3 scripts/atlas.py --check  # exit 1 if either is stale (CI)

Output:
    snippets/atlas.mdx  the matrix on Security policies, <Atlas />
    atlas.js            the same data for ui.js, which names each page's controls
"""
import json
import re
import sys

FRAMEWORKS = [
    # id (as the API names it), the accordion's title on the Frameworks page, a short label
    ("owasp-llm", "OWASP Top 10 for LLM Applications", "OWASP LLM"),
    ("owasp-agentic", "OWASP Top 10 for Agentic Applications", "OWASP Agentic"),
    ("mitre-atlas", "MITRE ATLAS", "MITRE ATLAS"),
    ("nist-ai-rmf", "NIST AI Risk Management Framework", "NIST AI RMF"),
    ("iso-42001", "ISO/IEC 42001", "ISO 42001"),
    ("eu-ai-act", "EU AI Act", "EU AI Act"),
    ("aws-security-hub", "AWS Security Hub", "AWS Security Hub"),
]

# The console's categories, in the order its Findings page lists them, each with the docs
# pages where a reader acts on what the category's policies find.
CATEGORIES = [
    ("GOV", "Governance", "Shadow assets, owners and unused agents", [("Registry", "/govern/registry"), ("Shadow AI", "/discover/shadow-ai")]),
    ("EXP", "Exposure", "Who can reach an asset, and from where", [("Control actions", "/govern/control-actions"), ("AI Inventory", "/discover/inventory")]),
    ("IAM", "Identity and access", "Whose credentials an agent acts with", [("People", "/discover/people"), ("Control actions", "/govern/control-actions")]),
    ("AGY", "Agency", "What an agent can do on its own", [("Control actions", "/govern/control-actions"), ("Findings", "/posture/findings")]),
    ("OBS", "Observability", "Whether anyone traces and scores an agent", [("Observability", "/monitor/observability"), ("Evals", "/monitor/evals")]),
    ("RT", "Runtime protection", "Whether calls pass a gateway or a guardrail", [("LLM gateway", "/runtime/llm-gateway"), ("Guardrails", "/runtime/guardrails")]),
    ("DAT", "Data and secrets", "Credentials in the open, and paths out", [("Findings", "/posture/findings"), ("Guardrails", "/runtime/guardrails")]),
    ("SUP", "Supply chain", "Components from outside the registry", [("Registry", "/govern/registry"), ("Security policies", "/posture/security-policies")]),
]

# Pages that speak for the whole posture name every framework.
WHOLE = ["/posture/findings", "/posture/security-policies", "/posture/frameworks"]

CODE = re.compile(r"^((?:GOVERN|MAP|MEASURE|MANAGE) \d+\.\d+|Art\. \d+|\S+)\s+(.*)$")


def policies():
    out = {}
    for line in open("posture/security-policies.mdx"):
        m = re.match(r"^\| ([A-Z]+-\d+) \| ([^|]+) \|", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def frameworks():
    text = open("posture/frameworks.mdx").read()
    out = {}
    for fid, title, _ in FRAMEWORKS:
        start = text.index(f'<Accordion title="{title}')
        body = text[start:text.index("</Accordion>", start)]
        rows = []
        for line in body.splitlines():
            m = re.match(r"^\| (.+?) \| ([A-Z]+-\d+(?:, [A-Z]+-\d+)*) \|$", line)
            if not m:
                continue
            c = CODE.match(m.group(1))
            rows.append({"code": c.group(1), "name": c.group(2), "policies": m.group(2).split(", ")})
        if not rows:
            sys.exit(f"atlas: no controls read for {title}")
        out[fid] = rows
    return out


def build():
    pol = policies()
    fw = frameworks()
    known = set(pol)
    for rows in fw.values():
        for r in rows:
            for p in r["policies"]:
                if p not in known:
                    sys.exit(f"atlas: {p} on the Frameworks page is not in the policy catalog")
    cats = []
    for prefix, name, line, pages in CATEGORIES:
        mine = sorted((p for p in pol if p.startswith(prefix + "-")), key=lambda p: int(p.split("-")[1]))
        cells = {}
        for fid, _, _ in FRAMEWORKS:
            cells[fid] = [
                {"code": r["code"], "name": r["name"], "policies": [p for p in r["policies"] if p in mine]}
                for r in fw[fid] if any(p in mine for p in r["policies"])
            ]
        cats.append({"id": prefix.lower(), "name": name, "line": line, "pages": pages,
                     "policies": [{"id": p, "title": pol[p]} for p in mine], "cells": cells})
    controls = sum(len(v) for v in fw.values())
    # Each page's controls: those of the categories that send readers to it.
    pages = {}
    for c in cats:
        for _, href in c["pages"]:
            pc = pages.setdefault(href, {})
            for fid, items in c["cells"].items():
                for it in items:
                    if it["code"] not in pc.setdefault(fid, []):
                        pc[fid].append(it["code"])
    for href in WHOLE:
        pages[href] = {fid: [r["code"] for r in fw[fid]] for fid, _, _ in FRAMEWORKS}
    data = {
        "frameworks": [{"id": f, "label": l, "count": len(fw[f])} for f, _, l in FRAMEWORKS],
        "categories": cats,
        "policies": len(pol),
        "controls": controls,
        "pages": pages,
    }
    return data


def mdx(data):
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return (
        "{/* Generated by scripts/atlas.py from posture/frameworks.mdx and posture/security-policies.mdx. Do not edit by hand. */}\n\n"
        f"export const ATLAS = {blob};\n\n"
        + ATLAS_JSX
    )


ATLAS_JSX = r'''export const Atlas = () => (
  <div className="oc-atlas" data-fw="all">
    <div className="oc-atlas-head">
      <div className="oc-atlas-count">
        <span><b>{ATLAS.policies}</b> security policies</span>
        <span><b>{ATLAS.controls}</b> framework controls</span>
        <span><b>{ATLAS.frameworks.length}</b> frameworks</span>
      </div>
      <div className="oc-atlas-pick" role="group" aria-label="Show one framework's controls">
        <button type="button" data-fw-pick="all" aria-pressed="true">All</button>
        {ATLAS.frameworks.map((f) => (
          <button type="button" key={f.id} data-fw-pick={f.id} aria-pressed="false">{f.label}</button>
        ))}
      </div>
    </div>
    <div className="oc-atlas-scroll">
      <table className="oc-atlas-grid">
        <thead>
          <tr>
            <th scope="col" className="oc-atlas-corner"><span className="oc-sr">Category</span></th>
            {ATLAS.frameworks.map((f) => (
              <th scope="col" key={f.id} data-fw-col={f.id}>{f.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ATLAS.categories.map((c) => (
            <tr key={c.id} className={"oc-cat-" + c.id}>
              <th scope="row">
                <a className="oc-atlas-cat" href={c.pages[0][1]} title={c.line}><i aria-hidden="true" />{c.name}</a>
              </th>
              {ATLAS.frameworks.map((f) => (
                <td key={f.id} data-fw-col={f.id}>
                  {c.cells[f.id].length ? (
                    <span className="oc-cell" title={c.cells[f.id].map((it) => it.code + " " + it.name).join("\n")}>
                      <span className="oc-n" data-n={Math.min(c.cells[f.id].length, 4)}>{c.cells[f.id].length}</span>
                      <span className="oc-codes">
                        {c.cells[f.id].map((it) => (
                          <span key={it.code} className="oc-ctl">{it.code.replace("BedrockAgentCore", "AgentCore")}</span>
                        ))}
                      </span>
                    </span>
                  ) : (
                    <span className="oc-ctl-none" aria-label="None">·</span>
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    <p className="oc-atlas-note">Each number counts the framework's controls that a category's policies answer. Pick a framework to see them.</p>
  </div>
);
'''


def js(data):
    slim = {"frameworks": data["frameworks"], "pages": data["pages"]}
    return (
        "// Generated by scripts/atlas.py. Do not edit by hand. ui.js reads it to name each page's controls.\n"
        f"window.__ocAtlas = {json.dumps(slim, ensure_ascii=False, separators=(',', ':'))};\n"
    )


def main():
    data = build()
    files = {"snippets/atlas.mdx": mdx(data), "atlas.js": js(data)}
    if "--check" in sys.argv:
        stale = [p for p, body in files.items() if open(p).read() != body]
        if stale:
            print("atlas: stale, run python3 scripts/atlas.py: " + ", ".join(stale), file=sys.stderr)
            sys.exit(1)
        print("atlas: current")
        return
    for p, body in files.items():
        with open(p, "w") as f:
            f.write(body)
    print(f"atlas: {data['policies']} policies, {data['controls']} controls, {len(data['frameworks'])} frameworks")


if __name__ == "__main__":
    main()
