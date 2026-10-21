# OpenController documentation

The customer documentation for OpenController, published with [Mintlify](https://mintlify.com).

- Pages are MDX files; navigation and settings are in `docs.json`.
- The API reference is generated from `api-reference/openapi.json`, which comes from the product's OpenAPI file.
- The product repository pins this repository as the submodule `docs/site`, so a checkout of the product carries the
  docs that match it.

## Preview

```
npm i -g mint
mint dev
```

Then open http://localhost:3000.

## Check

```
vale sync && vale .
mint broken-links
python3 scripts/check.py
python3 scripts/flags.py --check
```

CI runs the same on every pull request.

## Flags

`flags.json` turns parts of the site on and off. A part that is off is out of the navigation and its pages are
marked hidden, so they are neither listed, searched nor in the sitemap; the files stay in the repository. Change a flag, run `python3 scripts/flags.py` to apply it
to `docs.json`, and commit both.

| Flag | What it shows |
|---|---|
| `apiReference` | The API reference tab: the guide pages and the endpoints from `api-reference/openapi.json`. |
| `fineTuning` | The Fine-tuning page, in an Improve group before Ask Ctrl. |

## Generated pages

Three parts of the site are generated, never edited by hand, and CI fails when one is stale:

| Script | Writes | From |
|---|---|---|
| `scripts/diagrams.py` | `snippets/diagrams.mdx` | The drawings in the script. |
| `scripts/atlas.py` | `snippets/atlas.mdx`, `atlas.js` | The Frameworks page and the policy catalog on Security policies. |
| `scripts/roles.py` | `snippets/roles.mdx`, `roles.js` | The platform's permission catalogs, read from `../../services/platform` (or `OC_PLATFORM`), and `scripts/roles-pages.json`, which says which pages use which permissions. |

Pages do not repeat who can do what: the answer strip under each title names the roles, from `roles.js`, and the Roles page holds the full table. When a page starts using a permission, add it to `scripts/roles-pages.json` and run `python3 scripts/roles.py`.

## Diagrams

`scripts/diagrams.py` draws the diagrams as inline SVG into `snippets/diagrams.mdx`, in the console's palette
through CSS variables, so they stay sharp at any width and follow the theme. A page shows one with
`<Diagram name="traces" alt="..." />`. Edit the script, not the snippet.

## Publish

Mintlify's GitHub app watches this repository: every pull request gets a preview, and `main` is published.
