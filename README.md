# OpenController documentation

The customer documentation for OpenController, published with [Mintlify](https://mintlify.com).

- Pages are MDX files, organized by task: `get-started`, `discover`, `govern`, `secure`, `posture`, `monitor`,
  `administer`, and `integrations` (its own tab). Navigation and settings are in `docs.json`.
- Screenshots are in `images/`, beside the section they belong to.
- `style.css` and `ui.js` give the site its look; `snippets/` holds the walkthrough diagrams and the framework atlas.
- [STYLE.md](STYLE.md) is how the pages are written. It is not published.

The site before this structure is kept on the branch `archive/docs-v1`.

## Preview

```
npm i -g mint
mint dev
```

Then open http://localhost:3000.

## Check

```
mint validate
mint broken-links
```

CI runs the same on every pull request.
