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

`flags.json` turns parts of the site on and off. A part that is off is out of the navigation, so it is neither
listed nor searchable; its pages stay in the repository. Change a flag, run `python3 scripts/flags.py` to apply it
to `docs.json`, and commit both.

| Flag | What it shows |
|---|---|
| `apiReference` | The API reference tab: the guide pages and the endpoints from `api-reference/openapi.json`. |

## Diagrams

`scripts/diagrams.py` draws the diagrams as inline SVG into `snippets/diagrams.mdx`, in the console's palette
through CSS variables, so they stay sharp at any width and follow the theme. A page shows one with
`<Diagram name="traces" alt="..." />`. Edit the script, not the snippet.

## Publish

Mintlify's GitHub app watches this repository: every pull request gets a preview, and `main` is published.
