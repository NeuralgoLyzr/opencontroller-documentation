---
name: OpenController Docs
description: The OpenController console's identity, carried into its customer documentation on Mintlify.
colors:
  primary: "#3d5a86"
  primary-dark: "#9db2d4"
  primary-hover: "#4a6a9b"
  primary-hover-dark: "#b3c4df"
  primary-soft: "#e8edf5"
  primary-soft-dark: "#232a36"
  foreground: "#141311"
  foreground-dark: "#ebe8e3"
  muted-foreground: "#635d51"
  muted-foreground-dark: "#a39e95"
  muted: "#e8e4dd"
  muted-dark: "#23221f"
  border: "#e3ded4"
  border-dark: "#2a2926"
  border-strong: "#d2cdc0"
  border-strong-dark: "#38362f"
  sidebar: "#f8f7f4"
  sidebar-dark: "#1a1917"
  paper: "#ffffff"
  paper-dark: "#1a1917"
  ink-code: "#1a1917"
  ink-code-dark: "#121110"
  tone-green: "#3f7a4f"
  tone-green-dark: "#6faa83"
  tone-ochre: "#a5671c"
  tone-ochre-dark: "#cfa25a"
  tone-rust: "#9e3b28"
  tone-rust-dark: "#d4685a"
  tone-violet: "#7a5a8c"
  tone-violet-dark: "#ae92c9"
  tone-sienna: "#a0522d"
  tone-sienna-dark: "#cc8459"
  tone-teal: "#2f7a76"
  tone-teal-dark: "#6fb3ae"
  tone-rose: "#9b4d6e"
  tone-rose-dark: "#d08aa8"
typography:
  display:
    fontFamily: "Manrope, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(2rem, 1.4rem + 2vw, 2.75rem)"
    fontWeight: 700
    lineHeight: 1.08
    letterSpacing: "-0.03em"
  lead:
    fontFamily: "Manrope, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.5
  headline:
    fontFamily: "Manrope, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    letterSpacing: "-0.022em"
  title:
    fontFamily: "Manrope, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    letterSpacing: "-0.015em"
  body:
    fontFamily: "Manrope, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.7
    letterSpacing: "-0.005em"
    fontFeature: "\"ss01\", \"cv05\""
  nav:
    fontFamily: "Manrope, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 500
    letterSpacing: "-0.005em"
  label:
    fontFamily: "Manrope, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    letterSpacing: "0.04em"
  mono:
    fontFamily: "JetBrains Mono, ui-monospace, SF Mono, monospace"
    fontSize: "0.6875rem"
    fontWeight: 500
    lineHeight: 1.5
    fontFeature: "\"liga\" 0"
rounded:
  xs: "4px"
  sm: "calc(0.5rem - 2px)"
  md: "0.5rem"
  lg: "calc(0.5rem + 2px)"
  pill: "999px"
spacing:
  xs: "0.25rem"
  sm: "0.5rem"
  md: "0.75rem"
  lg: "1rem"
  xl: "1.25rem"
  2xl: "1.5rem"
  section: "3rem"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.paper}"
    typography: "{typography.nav}"
    rounded: "{rounded.md}"
    padding: "0 0.9rem"
    height: "2.25rem"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-secondary:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.md}"
    padding: "0 0.9rem"
    height: "2.25rem"
  card:
    backgroundColor: "{colors.sidebar}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.md}"
    padding: "1.125rem 1.25rem 1.25rem"
  panel:
    backgroundColor: "{colors.sidebar}"
    rounded: "{rounded.md}"
    padding: "1rem 1.5rem 1.25rem"
  nav-item:
    textColor: "{colors.foreground}"
    typography: "{typography.nav}"
    rounded: "{rounded.sm}"
    padding: "0 0.5rem"
    height: "2rem"
  nav-item-active:
    backgroundColor: "{colors.muted}"
    textColor: "{colors.foreground}"
  control-chip:
    backgroundColor: "{colors.sidebar}"
    textColor: "{colors.foreground}"
    typography: "{typography.mono}"
    rounded: "{rounded.xs}"
    padding: "0.05rem 0.375rem"
  role-chip:
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0 0.55rem"
    height: "1.5rem"
  framework-chip:
    backgroundColor: "{colors.sidebar}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.pill}"
    padding: "0 0.5rem"
    height: "1.5rem"
  method-tag:
    textColor: "{colors.paper}"
    typography: "{typography.mono}"
    rounded: "{rounded.xs}"
    padding: "0.05em 0.4em"
  atlas-count:
    textColor: "{colors.foreground}"
    rounded: "{rounded.sm}"
    padding: "0 0.375rem"
    height: "2rem"
    width: "2rem"
  framework-picker-active:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.paper}"
    rounded: "{rounded.sm}"
    padding: "0 0.625rem"
    height: "1.75rem"
  code-block:
    backgroundColor: "{colors.ink-code}"
    rounded: "{rounded.md}"
---

# Design System: OpenController Docs

## Overview

**Creative North Star: "The Console's Ledger"**

The docs are the OpenController console, opened to its paperwork. The same warm paper and slate, the same Manrope, the same side panel with its 2rem rows and muted section titles, so a reader moves from a console page to its documentation without a seam. What the console shows as live state, the docs show as ruled evidence: hairline tables, a framework matrix whose cells hold one count each, permission grids that shade the least role, control codes set as small keyed chips in mono.

Density is moderate and measured. Prose holds a reading measure (72ch body, 62ch lead) inside a wide 54rem column that sits against the sidebar; only the generated instruments (the atlas, the permission table) run the full width. Colour is scarce and always means something: slate for the one action and for selection, six soft capability tones for the console's sections, and two more (teal, rose) where the policy categories need eight. Everything else is warm neutral. Dark is the default appearance; light is a full peer, not an afterthought.

Surfaces are flat. Depth comes from a two-step paper (page paper and the slightly warmer sidebar tone), hairline borders, and tinted fills mixed from the tones, never from shadows on content. Motion is a quiet confirmation: a page rises 6px on arrival, diagrams draw in and run a signal along their lines, the walkthrough cycles on its own; all of it stops for readers who ask for less motion.

**Key Characteristics:**
- The console's identity, binding: warm neutrals, slate primary, Manrope and JetBrains Mono, soft capability tones.
- Ruled, tabular instruments over card grids; numbers in tabular figures.
- Tones applied as small marks and low-percentage tints, never as fills of body text or large pastel panels.
- Flat surfaces, hairline structure, a single radius family around 0.5rem.
- Dark default, light at parity; every tone has a tuned dark value.

## Colors

Warm paper neutrals carry everything; one desaturated slate acts; eight soft tones label sections and categories.

### Primary
- **Console Slate** (`primary`, dark `primary-dark`): the one action colour. The primary button, link text and its underline (at 45% mix, full on hover), the focus ring (2px outline, 2px offset), the caret, the picked framework in the atlas, the least-role shading in the permission table, the atlas count tints, and the fallback for any tone-driven element on an untoned page.
- **Slate Lift** (`primary-hover`, dark `primary-hover-dark`): the primary button's hover only.
- **Slate Wash** (`primary-soft`, dark `primary-soft-dark`): text selection and the default icon tile behind a card's mark.

### Secondary
The capability tones, one per console section, set on `<html data-tone>` by the page's path and inherited as `--oc-tone`:
- **Moss Green** (`tone-green`): Discover; viewer role; GET method; good callouts.
- **Ochre** (`tone-ochre`): Govern; operator role; PUT and PATCH; warning callouts.
- **Rust** (`tone-rust`): Control; admin role; DELETE; danger callouts.
- **Slate** (same as primary): Runtime, Integrations, Ask Ctrl; POST; info callouts.
- **Muted Violet** (`tone-violet`): Posture; owner role.
- **Sienna** (`tone-sienna`): Observe and Improve.

### Tertiary
- **Deep Teal** (`tone-teal`): the Observability policy category, and the team-scope badge in the permission table.
- **Dusty Rose** (`tone-rose`): the Supply chain policy category.

The eight policy categories map onto the tones as the console's Findings page colours them: Governance green, Exposure rust, Identity violet, Agency sienna, Observability teal, Runtime slate, Data ochre, Supply chain rose.

### Neutral
- **Ink** (`foreground`): all text and the closing rules of a table.
- **Warm Stone** (`muted-foreground`): leads, secondary text, table heads, answer-strip keys, inactive method tags.
- **Sand** (`muted`): the current sidebar row, inline code ground, hover fills, scrollbar thumb.
- **Hairline** (`border`): every structural rule and container edge.
- **Strong Hairline** (`border-strong`): empty-cell marks and "not held" marks in the instruments.
- **Sidebar Paper** (`sidebar`): navbar, sidebar, cards, panels, callouts, accordions, instrument heads.
- **Page Paper** (`paper`): the page ground and the body of the atlas and permission table. In dark mode it equals Sidebar Paper; tone separation there comes from hairlines alone.
- **Code Ink** (`ink-code`): every code block, in both modes.

### Named Rules
**The One Slate Rule.** Slate is the only colour that acts. One primary button per view; everything else that is clickable is ink on paper with a hairline that darkens on hover.

**The Tint, Not Pastel Rule.** A tone reaches a surface only through `color-mix` at `--oc-tint` (12% light, 16% dark) over transparent, or as a dot, a 2px line, an icon stroke. The build overrides Mintlify's Tailwind callout pastels to paper with a tinted icon tile; keep it that way.

**The Tone Means Section Rule.** A capability tone always names a console section, a role, a method or a policy category. Never pick a tone for decoration.

## Typography

**Display Font:** Manrope (with ui-sans-serif, system-ui)
**Body Font:** Manrope, with stylistic sets `ss01` and `cv05`
**Label/Mono Font:** JetBrains Mono (with ui-monospace, SF Mono), ligatures off

**Character:** One geometric-humanist sans does every job from display to the 11px section titles, tightened slightly as it grows. Mono is reserved for what a reader would type or match: code, paths, control codes, method tags, keycaps.

### Hierarchy
- **Display** (700, clamp 2rem to 2.75rem, 1.08, -0.03em, balanced): the page title, once per page.
- **Lead** (400, 1.125rem, 1.5, Warm Stone, 62ch, pretty): the description under the title.
- **Headline** (700, 1.5rem, -0.022em): section heads, each opened by a hairline rule 1.25rem above it and 3rem from the prior section.
- **Title** (600, 1.125rem, -0.015em): subsections; panel and card titles run 1 to 1.0625rem at 600.
- **Body** (400, 1rem, 1.7, 72ch): prose. Bold is 600, never 700.
- **Nav** (500, 0.8125rem): sidebar rows; section titles beneath them at 0.6875rem, 500, Warm Stone, sentence case.
- **Label** (600, 0.75rem, 0.04em, uppercase): table heads and the answer strip's keys (0.6875rem there). Instrument column heads drop the uppercase and tracking.
- **Mono** (500 to 600, 0.6875rem in chips and tags, 0.85em inline): code and data only.

### Named Rules
**The Mono Is Data Rule.** JetBrains Mono appears only on strings a reader types, copies or matches against the console. Prose, labels and numbers in counts stay in Manrope.

**The Tabular Figures Rule.** Every number in a table, count or chip uses `tabular-nums`, so columns of counts line up.

## Layout

A wide reading column (`--content-width` 54rem) sits against a 16rem sidebar with 3rem side padding from 1024px up; the leftover width falls to the right, past the table of contents. On wide-mode pages other than the home page, prose holds 46rem and only the atlas and permission table run full width. Paragraphs cap at 72ch.

Spacing is a rem rhythm of 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2 and 3rem. Containers pad 1.125 to 1.5rem; section breaks are 3rem; instrument cells pad 0.5 to 1rem.

The home page is a strip of actions (one slate button, one secondary, a one-line promise), the walkthrough panel, a three-column commitments strip with tone dots, and a ruled list of next pages with a drawn arrow. Card grids run three columns.

At 760px and below: grids and strips collapse to one column; the answer strip stacks; diagrams keep a 620px minimum and scroll sideways under a right-edge fade rather than shrink; a picked framework in the atlas shows only its column; the permission table becomes one card per permission with the four roles named on one line; the page-key hint hides.

## Elevation & Depth

Flat by default. Content surfaces (cards, panels, callouts, code blocks, tables, footer tiles) carry no shadow; Mintlify's card shadow is removed. Depth comes from two papers (page and sidebar), hairlines, and tone tints. Shadows exist only on things that float above the page, and as a tinted glow on a diagram node under the pointer.

### Shadow Vocabulary
- **Floating control** (`box-shadow: 0 2px 8px rgba(20, 19, 17, 0.08)`): the Ask the docs button.
- **Floating panel** (`box-shadow: 0 8px 32px rgba(20, 19, 17, 0.12)`): the Ask the docs panel.
- **Node glow** (`filter: drop-shadow(0 2px 6px color-mix(in srgb, var(--oc-tone) 28%, transparent))`): a diagram node on hover or focus, with its stroke in the tone.

### Named Rules
**The Lift Is A Pixel Rule.** Interactive containers answer hover with a border shift to the tone (or slate) and `translateY(-1px)`, never a shadow.

**The Keycap Rule.** Keyed chips (control codes, keyboard keys, inline codes in the answer strip and permission table) take a 1px hairline with a 2px bottom edge in the same hairline colour. This is the world's own chip device, not an offset shadow; keep it hairline-coloured and 2px.

## Shapes

One radius family around 0.5rem: containers at 0.5rem, inner tiles, nav rows and atlas counts 2px tighter, the atlas picker's track 2px looser, small chips and tags at 4px, roles, framework chips, play control and the floating button fully round. Mintlify's `rounded-xl` and `rounded-2xl` are forced back to 0.5rem. Diagram boxes use 6 to 10px radii and full pills for the OpenController node. Tone dots are circles; policy-category marks are 0.625rem squares at 2px radius.

## Components

### Buttons
- **Shape:** gently rounded (0.5rem), 2.25rem tall, 0.9rem side padding, 0.875rem at 600.
- **Primary:** Console Slate ground, paper text (Ink in dark mode). Hover moves to Slate Lift.
- **Secondary:** Page Paper ground, Ink text, hairline border that darkens to Warm Stone on hover.
- **Play control:** a 1.875rem pill on paper with a drawn play or pause mark; while playing it fills slate.
- **Focus:** a 2px slate outline at 2px offset on every link and button.

### Chips
- **Control chip:** mono 0.6875rem on Sidebar Paper, keycap edge, 4px radius. Lives in atlas cells once a framework is picked.
- **Role chip:** a pill in its role's tone at tint, text in the tone, capitalised; links to the role's row on the Roles page, gaining a 1px inset ring on hover.
- **Framework chip:** a hairline pill on Sidebar Paper with the framework's name and a muted count; the codes live in its title.
- **Method tag:** mono 0.6875rem uppercase-tracked, 4px radius, solid tone ground with paper text: GET green, POST slate, PUT and PATCH ochre, DELETE rust.

### Cards / Containers
- **Corner Style:** 0.5rem.
- **Background:** Sidebar Paper; the instruments use Page Paper with a Sidebar Paper head and note.
- **Shadow Strategy:** none (see Elevation).
- **Border:** 1px Hairline; on hover the section tone, or slate, with a 1px lift over 160ms.
- **Internal Padding:** 1.125rem by 1.25rem.
- **Card mark:** a 2.25rem tile tinted in the tone with the icon in the tone; provider marks sit on a paper tile with a hairline and take the page's ink.

### Callouts
Sidebar Paper with a hairline, never a pastel; the icon sits in a 1.75rem tile tinted with the callout's tone (ochre warning, rust danger, green good, slate info, stone neutral); the text stays Ink.

### Navigation
The console's side panel: Sidebar Paper with a hairline edge; rows 2rem high, 13px at 500, a 16px mark at 70% opacity; the current page on Sand in Ink, its mark at full strength in the section's tone; section titles at 11px in Warm Stone. The table of contents marks the current heading in the section tone. Mintlify's eyebrow above the title is hidden. The footer's previous and next links are hairline tiles with a `[` and `]` keycap hint.

### Answer Strip
Under every page title that has one: a hairline-topped row of key and value cells (In the console, Who can act, Framework controls). The console path is a crumb led by the page's sidebar mark in the tone, with drawn chevrons; roles show as role chips for the least role of each permission; framework chips link into the atlas with the framework picked.

### Control Framework Atlas
On Security policies: eight policy categories by seven frameworks, in a Page Paper container with a Sidebar Paper head carrying the counts line (bold tabular numerals) and a segmented framework picker. Each cell holds one count on a slate tint that deepens with the count (10, 22, 34, 46% over paper; 12, 24, 36% in dark), or a Strong Hairline mark when empty. Codes stay hidden at rest. Picking a framework lights its column on a 6% slate wash and opens its codes as control chips; the other columns recede. Category names link to their page with a drawn arrow that brightens and nudges 2px on hover.

### Permission Table
On Roles: sections of permissions in mono keycaps with a summary and where-links, against four role columns. A check marks each holding role; the least role that holds it is shaded at 8% slate with a slate check; roles that do not hold it show a Strong Hairline mark. A targeted row takes the same 8% wash. The head stays sticky.

### Walkthrough Panel
A Sidebar Paper panel of tabs over drawn diagrams. It cycles every 4.2s while at least a third of it is on screen, with a 2px tone line filling under the active tab; a tab clicked by hand restarts the clock; arrow keys step; leaving the screen or the browser tab pauses it. Readers who ask for less motion start paused.

### Diagrams
Inline SVG drawn by a script in their own `--oc-dg-*` palette, Manrope labels at 9.5 to 12.5px. A diagram waits at 25% until it scrolls into view, then its parts arrive in drawing order (18ms stagger, 520ms), a signal runs each line the way it points, and OpenController's pill breathes; off screen it pauses. Hovering a node lights it in the tone, dims its siblings to 55%, and washes every paragraph or row that names it at 10%.

### Reading Line
A 2px line fixed at the top of the viewport in the section's tone, scaling from left as the reader moves down the page.

## Do's and Don'ts

### Do:
- **Do** carry every colour through the `--oc-*` custom properties, with a dark value for each.
- **Do** keep one slate primary button per view; pair it with a secondary on paper.
- **Do** apply tones as dots, 2px lines, icon strokes and `color-mix` tints at `--oc-tint`.
- **Do** set code, paths, control codes, method tags and keycaps in JetBrains Mono with ligatures off, and everything else in Manrope.
- **Do** close tables with an Ink rule under the head and after the last row, hairlines between.
- **Do** use the shared ease `cubic-bezier(0.16, 1, 0.3, 1)` at 120 to 180ms for states and 320 to 520ms for arrivals, and stop all of it under `prefers-reduced-motion: reduce`.
- **Do** let diagrams scroll sideways on a phone under an edge fade rather than shrink their labels.
- **Do** draw icons as stroked SVG at 1.75 to 2.25 stroke, from the console's Lucide set or the console's own provider marks.

### Don't:
- **Don't** put shadows on cards, panels, callouts or code blocks; a hover lifts 1px and changes its border.
- **Don't** use Mintlify's Tailwind pastels for callouts or any surface.
- **Don't** introduce a tone that does not name a section, role, method or policy category.
- **Don't** put codes in atlas cells at rest; a cell holds one count, and the codes open only for a picked framework.
- **Don't** show an eyebrow or kicker above a page title; the sidebar already says where the reader is.
- **Don't** use sparkle icons on AI or assistant actions; the assistant's mark is a message circle with a question mark.
- **Don't** set prose or labels in mono.
- **Don't** edit the generated snippets (atlas, roles, diagrams) by hand; change the script that draws them.
