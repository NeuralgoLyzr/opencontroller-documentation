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

## The container

`Dockerfile` builds the site as a container: the pages exported by `mint export` (nothing of Mintlify's runs
afterwards), served by nginx with the rules the export asks for (`docker/nginx.conf`). CI builds it on every
pull request, and on every push to main publishes it to Lyzr Artifactory, the registry customers pull from, as
`opencontroller/docs:v0-<commit>`. A customer's cell runs it at the tag its values pin (`docs_host` and
`image_tags.docs` in the customer stack), and the console's sidebar links to it.

It loads nothing from anywhere else: the export bundles its assets, JetBrains Mono is kept in `fonts/` (Open Font
License), a build fails if a page names a font elsewhere, and nginx's Content-Security-Policy holds the browser to it.

It is held to the cell's license: with `LICENSE_API_URL`, which the chart sets, each page asks the cell's API first, and a
locked cell shows a locked page. An API that is down or restarting does not stop the pages. `/healthz` is for probes.

```sh
docker build -t opencontroller-documentation .
docker run --rm -p 8081:8080 opencontroller-documentation   # http://localhost:8081
```
