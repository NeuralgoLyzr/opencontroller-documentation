# OpenController documentation

The customer documentation for OpenController, published with [Mintlify](https://mintlify.com).

- Pages are MDX files; navigation and settings are in `docs.json`.
- The API reference is generated from `api-reference/openapi.json`, which `scripts/openapi.py` builds from the product's
  OpenAPI file (`services/platform/docs/swagger.json`, beside this site when it is checked out as the product's submodule).
  Run it after the product's API changes, and commit the result.
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
python3 scripts/openapi.py --check
```

CI runs the same on every pull request.

## Flags

`flags.json` turns parts of the site on and off. A part that is off is out of the navigation and its pages are
marked hidden, so they are neither listed, searched nor in the sitemap; the files stay in the repository. Change a flag, run `python3 scripts/flags.py` to apply it
to `docs.json`, and commit both.

| Flag | What it shows |
|---|---|
| `apiReference` | The API reference tab: the guide pages and the endpoints from `api-reference/openapi.json`. It also writes `snippets/api-link.mdx`, the `<ApiLink />` a page closes with: a link to the reference while on, nothing while off. |
| `fineTuning` | The Fine-tuning page, in an Improve group before Ask Ctrl. |

## Generated pages

Three parts of the site are generated, never edited by hand, and CI fails when one is stale:

| Script | Writes | From |
|---|---|---|
| `scripts/diagrams.py` | `snippets/diagrams.mdx` | The drawings in the script. |
| `scripts/atlas.py` | `snippets/atlas.mdx` | The Frameworks page and the policy catalog on Security policies. |
| `scripts/roles.py` | `snippets/roles.mdx` | The platform's permission catalogs, read from `../../services/platform` (or `OC_PLATFORM`), and `scripts/roles-pages.json`, which says which pages use which permissions. |

Pages do not say who can do what; the Roles page holds the full table, and each permission's row links to the pages that use it. When a page starts using a permission, add it to `scripts/roles-pages.json` and run `python3 scripts/roles.py`.

## Diagrams

`scripts/diagrams.py` draws the diagrams as inline SVG into `snippets/diagrams.mdx`, in the console's palette
through CSS variables, so they stay sharp at any width and follow the theme. A page shows one with
`<Diagram name="traces" alt="..." />`. Edit the script, not the snippet.

## Publish

Mintlify's GitHub app watches this repository: every pull request gets a preview, and `main` is published.

## The container

`Dockerfile` builds the site as a container: the pages exported by `mint export` (nothing of Mintlify's runs
afterwards), served by nginx with the rules the export asks for (`docker/nginx.conf`). The product's CI builds it
from this repository's pinned commit (the submodule `docs/site`) with the cell's other images, and the cell runs it
beside the console (`docs.enabled` in the Helm chart, the `docs` service in Compose), where the console's
Documentation button opens it.

```sh
docker build -t opencontroller-documentation .
docker run --rm -p 8083:8080 opencontroller-documentation   # http://localhost:8083
```
