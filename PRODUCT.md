# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Security, AI-platform, and governance, risk and compliance leaders, who evaluate OpenController and govern their organization's AI with it. Then the administrators and operators who install it, connect the clouds, and run it day to day. The pages never name their audience; they speak to the reader in the second person.

## Product Purpose

OpenController is the control plane for an organization's AI agents. It finds every agent and everything each agent uses across the organization's clouds, gives each one an owner and a standing in a registry, and holds the authority to stop the ones that should not run. These docs explain what it does, how to roll it out, and how to operate every page of the console. Success is a reader who can explain the product to a peer and an admin who can connect a cloud and act on what discovery finds without asking anyone.

## Positioning

- **One inventory, every cloud.** Every AI agent and everything it uses, across AWS, Microsoft, Google Cloud, Databricks, Anthropic and Snowflake, in one inventory and one map.
- **Authority to stop.** Not only visibility: register, approve, block, quarantine and delete on the platform the agent runs on, every action audited.
- **Read-only by default.** Discovery never invokes an agent, reads a conversation or fetches a secret. Control is a second credential, granted per platform.
- **Runs in your environment.** Ships on-premises, one installation per organization, secrets in HashiCorp Vault, traces in the customer's own store.

## Operating Context

Readers arrive from the console, from a rollout plan, or from search, usually with one question about one page. The docs mirror the console's sidebar: Discover, Govern, Control, Observe, Evaluate, the LLM gateway and guardrails, Posture, Improve, Integrations. Each page names the permissions and roles that can act.

## Capabilities and Constraints

- Hosted on Mintlify: MDX pages, `docs.json`, custom CSS (`style.css`) and custom JS (`ui.js`, `assistant.js`). No separate framework or site.
- The API reference is behind a flag (`flags.json`, `scripts/flags.py`) and stays off until the flag turns it on.
- House writing style: Google developer style plus the OpenController Vale rules, US English, Diátaxis structure.
- Diagrams are drawn by `scripts/diagrams.py` as inline SVG; never edit the generated snippet.
- The docs assistant goes through OpenController's own LLM gateway, not Mintlify's; it stays inert until configured.

## Brand Commitments

- The console's identity is binding: its warm neutrals, slate primary, Manrope and JetBrains Mono, its soft capability tones, and its sidebar marks.
- No sparkle icons on AI or assistant actions; the assistant's mark is a message circle with a question mark.
- Never name reference or internal projects in the docs.

## Evidence on Hand

- Drawn diagrams of the system, the registry states, the two credentials, the gateway, traces and evals (`scripts/diagrams.py`).
- The console's provider marks (`snippets/logos.mdx`).
- No screenshots or names from customer or preview tenants may appear. Any product visual is drawn or synthetic, and labelled as such where it could be mistaken for real data.
- No customer logos, testimonials, benchmarks or pricing exist for the docs to use.

## Product Principles

1. Lead with what is true and checkable: what discovery reads, what control changes, who can act.
2. Every page answers one reader's question; the console is the map of the docs.
3. Safety is shown, not claimed: read-only first, control opt-in, every action audited.
4. One identity across the console and the docs, so a reader moves between them without a seam.
