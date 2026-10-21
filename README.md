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
```

CI runs the same on every pull request.

## Publish

Mintlify's GitHub app watches this repository: every pull request gets a preview, and `main` is published.
