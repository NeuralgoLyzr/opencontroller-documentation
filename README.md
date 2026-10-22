# OpenController documentation

The customer documentation for OpenController, published with [Mintlify](https://mintlify.com).

- Pages are MDX files, organized by task: `get-started`, `discover`, `govern`, `secure`, `posture`, `monitor`,
  `administer`, and `integrations` (its own tab). Navigation and settings are in `docs.json`.
- Screenshots are in `images/`, beside the section they belong to.
- `style.css` and `ui.js` give the site its look; `snippets/` holds the walkthrough diagrams and the framework atlas.
- [STYLE.md](STYLE.md) is how the pages are written. It is not published.

The site before this structure is kept on the branch `archive/docs-v1`.

## Versions

`docs.json` lists the documented versions under `navigation.versions`; the one marked `"default": true` (tag
`Latest`) is what readers see first. Add a version only when a release changes the docs enough to matter, not for every
patch. When one does:

1. Copy the pages of the current version into a folder named after it, for example `v0.108/`, and point that version's
   entry in `docs.json` at the copies (`v0.108/get-started/quickstart`, …). Drop its `default` and `tag`.
2. Add the new version at the top of `navigation.versions`, with `"tag": "Latest"` and `"default": true`, using the
   pages at the root, which go on changing.
3. Run `mint broken-links`: links inside the copied pages must point into their own folder.

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
