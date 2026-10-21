#!/usr/bin/env python3
"""Builds the permission table on the Roles page from the platform's source.

Every module of the platform declares its permissions in a catalog: the
permission, the least built-in role that holds it, a one-line summary, and
whether a role in a team holds it too. This reads those catalogs from the Go
source, so the docs never restate them by hand. Which docs pages use which
permissions is kept in scripts/roles-pages.json.

The platform lives beside these docs in the product repository, at
../../services/platform; set OC_PLATFORM to read it from elsewhere. Run from
the site's root:

    python3 scripts/roles.py          # write snippets/roles.mdx
    python3 scripts/roles.py --check  # exit 1 if either is stale

Without the platform's source (as in this repository's own CI), --check
compares the generated files with each other and with roles-pages.json only.
"""
import glob
import json
import os
import re
import sys

PLATFORM = os.environ.get("OC_PLATFORM", os.path.join(os.path.dirname(__file__), "..", "..", "..", "services", "platform"))

ROLES = [
    ("viewer", "Viewer"),
    ("operator", "Operator"),
    ("admin", "Admin"),
    ("owner", "Owner"),
]
RANK = {r: i for i, (r, _) in enumerate(ROLES)}

# What every signed-in person holds, whatever their role (access.Everyone).
EVERYONE = ["me:read", "me:write"]

# The table's sections, in the order of the docs' navigation, each the resources it holds.
SECTIONS = [
    ("Inventory and discovery", ["assets", "graph", "scans", "connections"]),
    ("Spend", ["spend"]),
    ("Registry and control", ["registry", "ownership", "actions"]),
    ("Posture", ["posture"]),
    ("LLM gateway and guardrails", ["modules", "gateway", "guardrails"]),
    ("Observability", ["observability"]),
    ("Ask Ctrl", ["chat"]),
    ("Organization and access", ["org", "features", "users", "service-accounts", "teams", "directory", "sso", "access", "secrets", "settings", "audit", "me"]),
]

ENTRY = re.compile(
    r'("[a-z][a-z0-9-]*:[a-z][a-z0-9-]*"|[A-Za-z_][A-Za-z0-9_.]*)\s*:\s*\{\s*Role:\s*access\.(Viewer|Operator|Admin|Owner)'
    r'\s*,\s*Summary:\s*"((?:[^"\\]|\\.)*)"(\s*,\s*Teams:\s*true)?\s*\}'
)
CONST = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\s+(?:access\.Permission\s+)?=\s*"([a-z][a-z0-9-]*:[a-z][a-z0-9-]*)"')


def sources():
    files = glob.glob(os.path.join(PLATFORM, "cmd", "**", "*.go"), recursive=True)
    files += glob.glob(os.path.join(PLATFORM, "internal", "**", "*.go"), recursive=True)
    return [f for f in files if not f.endswith("_test.go") and "accesstest" not in f]


def catalog():
    files = sources()
    if not files:
        return None
    consts = {}
    for f in files:
        for name, value in CONST.findall(open(f).read()):
            consts.setdefault(name, set()).add(value)
    out = {}
    for f in files:
        for key, role, summary, teams in ENTRY.findall(open(f).read()):
            if key.startswith('"'):
                perm = key.strip('"')
            else:
                values = consts.get(key.split(".")[-1], set())
                if len(values) != 1:
                    sys.exit(f"roles: cannot resolve {key} in {os.path.relpath(f, PLATFORM)}")
                perm = next(iter(values))
            entry = {"id": perm, "role": role.lower(), "summary": summary.replace('\\"', '"'), "teams": bool(teams)}
            if perm in out and out[perm] != entry:
                sys.exit(f"roles: {perm} is described twice, differently")
            out[perm] = entry
    return out


def titles():
    # Pages a flag has hidden (hidden: true) are not offered as places a permission applies.
    out = {}
    for f in glob.glob("**/*.mdx", recursive=True):
        text = open(f).read()
        m = re.search(r'^title:\s*"([^"]+)"', text, re.M)
        if m and not re.search(r"^hidden: true$", text, re.M):
            out["/" + f[:-4]] = m.group(1)
    return out


def build(cat):
    pages = json.load(open("scripts/roles-pages.json"))
    names = titles()
    where = {}
    for page, perms in pages.items():
        if page not in names:
            continue
        for p in perms:
            where.setdefault(p, []).append([names[page], page])
    placed = set()
    sections = []
    for title, resources in SECTIONS:
        rows = sorted((e for e in cat.values() if e["id"].split(":")[0] in resources),
                      key=lambda e: (resources.index(e["id"].split(":")[0]), RANK[e["role"]], e["id"]))
        for e in rows:
            e["where"] = sorted(where.get(e["id"], []))
            e["everyone"] = e["id"] in EVERYONE
            placed.add(e["id"])
        if rows:
            sections.append({"id": re.sub(r"[^a-z]+", "-", title.lower()).strip("-"), "title": title, "rows": rows})
    missing = sorted(set(cat) - placed)
    if missing:
        sys.exit("roles: no section holds " + ", ".join(missing) + "; add its resource to SECTIONS")
    unknown = sorted({p for ps in pages.values() for p in ps} - set(cat))
    if unknown:
        sys.exit("roles: roles-pages.json names permissions the platform does not have: " + ", ".join(unknown))
    return {"roles": [{"id": r, "label": l} for r, l in ROLES], "sections": sections,
            "count": len(cat), "pages": pages}


JSX = r'''export const RoleTable = () => (
  <div className="oc-roles">
    <div className="oc-scroll">
      <table className="oc-roles-grid">
        <thead>
          <tr>
            <th scope="col">Permission</th>
            {ROLE_DATA.roles.map((r) => (<th scope="col" key={r.id} className="oc-roles-col">{r.label}</th>))}
          </tr>
        </thead>
        {ROLE_DATA.sections.map((s) => (
          <tbody key={s.id}>
            <tr className="oc-roles-section"><th scope="rowgroup" colSpan={ROLE_DATA.roles.length + 1} id={"perm-" + s.id}>{s.title}</th></tr>
            {s.rows.map((e) => (
              <tr key={e.id} id={"perm-" + e.id.replace(":", "-")}>
                <th scope="row">
                  <code>{e.id}</code>
                  {e.teams ? <span className="oc-roles-team" title="A role in a team holds this too, for what the team owns">Teams</span> : null}
                  <span className="oc-roles-sum">{e.summary}.</span>
                  {e.where.length ? (
                    <span className="oc-roles-where">{e.where.map((w) => (<a key={w[1]} href={w[1]}>{w[0]}</a>))}</span>
                  ) : null}
                </th>
                {ROLE_DATA.roles.map((r, i) => {
                  const least = ROLE_DATA.roles.findIndex((x) => x.id === e.role);
                  const held = e.everyone || i >= least;
                  return (
                    <td key={r.id} data-role={r.label} className={held ? (i === least && !e.everyone ? "oc-held oc-least" : "oc-held") : "oc-not"} aria-label={held ? r.label + " holds it" : r.label + " does not"}>
                      {held ? <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5" /></svg> : <span aria-hidden="true">·</span>}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        ))}
      </table>
    </div>
  </div>
);
'''


def outputs(data):
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    mdx = ("{/* Generated by scripts/roles.py from the platform's permission catalogs. Do not edit by hand. */}\n\n"
           f"export const ROLE_DATA = {blob};\n\n" + JSX)
    return {"snippets/roles.mdx": mdx}


def main():
    check = "--check" in sys.argv
    cat = catalog()
    if cat is None:
        if not check:
            sys.exit(f"roles: no platform source at {PLATFORM}; set OC_PLATFORM")
        # No platform here: the committed data must at least agree with roles-pages.json.
        snippet = open("snippets/roles.mdx").read()
        data = json.loads(re.search(r"export const ROLE_DATA = (\{.*?\});\n", snippet, re.S).group(1))
        if data["pages"] != json.load(open("scripts/roles-pages.json")):
            print("roles: stale against roles-pages.json; run python3 scripts/roles.py beside the platform", file=sys.stderr)
            sys.exit(1)
        print("roles: platform source not here; checked against roles-pages.json only")
        return
    files = outputs(build(cat))
    if check:
        stale = [p for p, body in files.items() if not os.path.exists(p) or open(p).read() != body]
        if stale:
            print("roles: stale, run python3 scripts/roles.py: " + ", ".join(stale), file=sys.stderr)
            sys.exit(1)
        print("roles: current")
        return
    for p, body in files.items():
        with open(p, "w") as f:
            f.write(body)
    print(f"roles: {len(cat)} permissions from the platform")


if __name__ == "__main__":
    main()
