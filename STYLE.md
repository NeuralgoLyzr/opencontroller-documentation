# Writing and page rules

Every page in these docs follows this file. `PLAN.md` says which pages exist and which template each uses.

## Readers

Security and platform admins, AI and platform engineers, reviewers. Many read English as a second language:
write plainly.

## Words

- Short sentences. One idea each. Present tense, active voice, "you".
- UI labels exactly as on screen, in bold: Select **New key**.
- Paths with `>`: Go to **LLM Gateway** > **Virtual Keys**.
- Roles as in the console: **Viewer**, **Operator**, **Admin**, **Owner**.
- No "simply", "just", "easy", "obviously". No marketing words ("powerful", "seamless").
- Say what a thing is for before how to use it.
- Use the same word for the same thing on every page (see Glossary).
- Never real customer data, real emails, account IDs or key values, and never name an organization, real or made
  up. Use `example.com` addresses (`alice@example.com`, `console.example.com`), `your-org.okta.com` style
  placeholders, agents `support-bot`, `billing-agent`, key values masked: `sk-bf-…abcd`.

## Page frontmatter

```mdx
---
title: "Virtual keys"            # the console label when the page is about a console page
description: "One sentence: what the reader gets from this page."
---
```

## Under the title

A role badge and, when a module must be on, a note:

```mdx
<Badge>Admin</Badge>

<Note>Needs the **LLM Gateway** module. See [Modules](/user-guide/settings/modules).</Note>
```

## Screenshots: one fixed format

Every screenshot spot is written exactly like this, so the list in `screenshots.md` can be built from the pages and
the images dropped in later by file name:

```mdx
{/* SCREENSHOT: vk-form | crop | The New key dialog, filled in for support-bot: May call (openai on), Budget $50 a month, Rate limit. */}
<Frame caption="The New key dialog">
  <img src="/images/llm-gateway/vk-form.png" alt="The New key dialog with access, budget and rate limit filled in." />
</Frame>
```

- `id`: lowercase, hyphens, unique across the site. The image file is `/images/<area>/<id>.png`.
- `full` = the whole page (only once, at the top of an overview page); `crop` = only the part the text is about.
- The description says exactly what to capture: which screen, which state, which example data, what to crop to.
- `alt`: what the image is for, one sentence, ≤ 155 characters, ends with a period.
- Put the screenshot right after the sentence that first mentions that screen.
- A tall or narrow screenshot (a card, a dialog, a side panel) goes without `<Frame>`, centered, at a fixed
  width so it is not stretched to the page's full width (340–480px, by what is readable):
  `<img className="w-[340px] mx-auto rounded-xl border border-gray-200 dark:border-gray-700" src="…" alt="…" />`
- No screenshot for text, code, JSON or terminal output. Write those as text or code blocks.
- Diagrams use Mermaid in a fenced ```` ```mermaid ```` block, not screenshots.

## Components

- `<Steps>` / `<Step title="…">` for any task of 2+ steps.
- `<Note>` prerequisites, `<Tip>` shortcuts, `<Warning>` something lost or exposed (e.g. a key shown once),
  `<Info>` background. One idea per callout.
- `<AccordionGroup>` / `<Accordion title="…">` for FAQ.
- `<CardGroup cols={2}>` / `<Card title="…" icon="…" href="…">` for Next steps.
- `<Tabs>` / `<Tab title="…">` for alternatives (console vs API, one provider vs another).
- `<CodeGroup>` for the same request in several languages.
- Internal links are root-relative without `.mdx`: `/user-guide/llm-gateway/virtual-keys`.

## Accuracy

- Only describe what the product does. Labels, fields, options and roles come from the console source and the
  platform README, not from memory.
- If something cannot be confirmed from the source, write it anyway in the best form and add
  `{/* TODO verify: what to check */}` right after it.

## Glossary (use these words)

| Term | Meaning |
|---|---|
| OpenController | The product. "the console" is its web app. |
| asset | Anything discovered: an agent, a model, an app, a key, a tool. |
| agent | An AI agent found by discovery or registered. |
| shadow AI | AI in use that is not registered. |
| registry | The list of registered (approved) agents. |
| integration | A connection to a cloud or SaaS account (Integrations page). |
| scan | Discovery reading an integration. |
| finding | A posture problem found on an asset. |
| LLM gateway | The gateway apps call models through (Rekori). |
| virtual key | A key an app uses to call the LLM gateway. |
| guardrail | A set of checks prompts and answers are held to. |
| check | One test inside a guardrail (personal data, prompt injection, …). |
| content rule | A rule in the LLM gateway that runs a guardrail on calls, to block or redact. |
| violation | A block or redaction a content rule made. |
| identity provider | A sign-in service (Okta, Entra ID, Auth0, Keycloak) that issues tokens. |
| module | An optional part that can be on or off for an organization (LLM Gateway, Observability, Evals, Fine-tuning, Guardrails). |
| service account | A non-human account with an API key, for apps and automation. |

## Look (the console's own, from opencontroller-documentation)

The site carries the OpenController console's look, the same as `~/Documents/opencontroller-documentation`
(its `DESIGN.md` is the full design system). `style.css`, `ui.js`, `favicon.svg` and `logo/` are copied from there;
change them there first, then copy them here.

| | Rule |
|---|---|
| Theme (`docs.json`) | Mintlify **mint** (our layout; only their colours, type and icons are taken), dark by default, light at parity. Primary slate `#3d5a86` (dark `#9db2d4`); page `#ffffff` light, `#1a1917` dark. |
| Colours | Warm neutrals and one slate that acts. Each section has a tone, set on `<html data-tone>` by `ui.js` from the page's path: Discover green, Govern ochre, Secure and Integrations slate, Posture violet, Monitor sienna. Tones only as dots, 2px lines, icon strokes and light tints. |
| Type | Manrope for all text, JetBrains Mono for code, paths and keys only. |
| Icons | Lucide (`"icons": {"library": "lucide"}`). Every page has an `icon:` in its frontmatter for the sidebar; card icons are Lucide names too. No brand logos. |
| Surfaces | Flat: hairline borders, no shadows on cards, callouts or code blocks. |
| Images | Screenshots of the product only. No AI-generated photography. |
| Copy | Fit the space: shorten the words, never shrink or condense the type. |
