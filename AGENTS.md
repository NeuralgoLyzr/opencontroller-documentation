# Documentation project instructions

This is OpenController's customer documentation, a Mintlify site. Pages are MDX with YAML frontmatter; navigation
and settings live in `docs.json`. The product's source is pinned beside this site in the product repository, which
carries these docs as a submodule at `docs/site`; the API reference is generated from the product's OpenAPI file.

## Audience

Security and platform administrators at a customer, and the partner engineers who deploy OpenController for them.
Assume they have never seen the product.

## Style

The house style is the [Google developer documentation style guide](https://developers.google.com/style), checked
by Vale (`.vale.ini`, `styles/`), plus these rules of our own:

- Second person, active voice, present tense, sentence case for headings. One idea per sentence, under 25 words.
- One term, one meaning. The [glossary](get-started/glossary.mdx) is the list; the console's label is the term.
  `styles/OpenController/Terms.yml` turns the common near-misses into errors.
- UI labels verbatim as the console shows them, in bold: Click **Register**.
- Code formatting for file names, commands, paths, environment variables, values keys and API paths.
- Explain what a thing is for before how to use it, then the procedure or the reference.
- Where a permission gates a page or action, name it.
- No em-dashes, no filler, no hedging, no roadmap. The rules in `styles/OpenController/` say which words.

## Structure

Pages follow [Diátaxis](https://diataxis.fr): each page is one of four kinds, and does not mix them.

| Kind | Answers | Here |
|---|---|---|
| Tutorial | "Take me through it once" | The quickstart, the rollout plan |
| How-to | "How do I do X" | The procedures on each module page, the connection guides |
| Reference | "What exactly is this" | Columns, settings, checks, policies, the API reference, the glossary |
| Explanation | "Why is it like this" | What is shadow AI, how it works, responding to discoveries |

A module page may hold a how-to and a reference under separate headings. Explanation never goes on a reference page.

## Checks

```
vale sync && vale .        # style
mint broken-links          # links
python3 scripts/check.py   # navigation, frontmatter, internal links, images
python3 scripts/flags.py --check   # docs.json matches flags.json
```

CI runs all four on every pull request and on `main`. `flags.json` turns parts of the site on and off (the API
reference, for one); apply a change with `python3 scripts/flags.py`. Diagrams are drawn by `scripts/diagrams.py`
into `snippets/diagrams.mdx`; edit the script, never the snippet.

## Content boundaries

- Document only what the product does. A missing detail beats an invented one.
- No customer, prospect or partner names; no names from any demo tenant's data; no internal environment names or
  URLs; no secrets or realistic-looking keys.
- No roadmap or "coming soon".
