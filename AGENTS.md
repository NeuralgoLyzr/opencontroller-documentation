# Documentation project instructions

This is OpenController's customer documentation, a Mintlify site. Pages are MDX with YAML frontmatter; navigation
and settings live in `docs.json`. The product's source is pinned beside this site in the product repository, which
carries these docs as a submodule at `docs/site`; the API reference is generated from the product's OpenAPI file.

## Audience

Security and platform administrators at a customer, and the partner engineers who deploy OpenController for them.
Assume they have never seen the product.

## Style

- Second person, active voice, sentence case for headings and UI labels. One idea per sentence.
- UI labels verbatim as the console shows them, in bold: Click **Register**.
- Code formatting for file names, commands, paths, environment variables, values keys and API paths.
- Explain what a thing is for before how to use it, then the procedure or the reference.
- Where a permission gates a page or action, name it.
- No em-dashes.

## Content boundaries

- Document only what the product does. A missing detail beats an invented one.
- No customer, prospect or partner names; no names from any demo tenant's data; no internal environment names or
  URLs; no secrets or realistic-looking keys.
- No roadmap or "coming soon".
