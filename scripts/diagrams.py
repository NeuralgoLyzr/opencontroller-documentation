#!/usr/bin/env python3
"""Draws the site's diagrams and renders them to PNG, light and dark.

Each diagram is laid out by hand here, with the console's palette, Manrope
and JetBrains Mono, and rendered at 2x through headless Chrome so the fonts
are real. Run from the site's root:

    python3 scripts/diagrams.py            # every diagram, both themes
    python3 scripts/diagrams.py system     # one diagram

Output: images/diagrams/<name>-light.png and <name>-dark.png, embedded in
the pages as two <img> tags, one shown per theme.
"""
import os
import subprocess
import sys
import tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = os.path.join(os.path.dirname(__file__), "..", "images", "diagrams")

# The console's tokens (apps/console/src/index.css), by theme.
THEMES = {
    "light": dict(bg="#ffffff", fg="#141311", muted_fg="#635d51", surface="#f8f7f4", muted="#e8e4dd",
                  border="#e3ded4", border_strong="#d2cdc0", primary="#3d5a86", primary_fg="#fdfcf9",
                  alt="#a0522d", ok="#3f7d5a", line="#a39e95"),
    "dark": dict(bg="#1a1917", fg="#ebe8e3", muted_fg="#a39e95", surface="#1f1e1b", muted="#23221f",
                 border="#2a2926", border_strong="#38362f", primary="#9db2d4", primary_fg="#121110",
                 alt="#cc8459", ok="#7fb894", line="#635d51"),
}
FONT = "Manrope, ui-sans-serif, system-ui, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, monospace"


class Canvas:
    def __init__(self, w, h, t):
        self.w, self.h, self.t = w, h, t
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    # A text run. anchor: start | middle | end.
    def text(self, x, y, s, size=12, weight=500, color=None, anchor="start", mono=False, spacing=None):
        color = color or self.t["fg"]
        fam = MONO if mono else FONT
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        self.add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
                 f'fill="{color}" text-anchor="{anchor}"{ls}>{esc(s)}</text>')

    # A group: a soft panel with a small label above its content.
    def group(self, x, y, w, h, label=None):
        t = self.t
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{t["surface"]}" stroke="{t["border"]}"/>')
        if label:
            self.text(x + 12, y + 18, label, size=11, weight=700, color=t["muted_fg"], spacing="0.04em")

    # A chip: a small bordered box with a label and an optional provider mark.
    def chip(self, x, y, w, h, label, logo=None, mono=False, strong=False):
        t = self.t
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{t["bg"]}" stroke="{t["border_strong"]}"/>')
        tx = x + 10
        if logo:
            self.add(LOGOS[logo](x + 9, y + (h - 16) / 2, t))
            tx = x + 31
        self.text(tx, y + h / 2 + 4, label, size=11.5, weight=600 if strong else 500, mono=mono)

    # A node: a card with a title and an optional second line.
    def node(self, x, y, w, h, title, sub=None, accent=None):
        t = self.t
        stroke = accent or t["border_strong"]
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{t["bg"]}" stroke="{stroke}"/>')
        if sub:
            self.text(x + w / 2, y + h / 2 - 2, title, size=12.5, weight=700, anchor="middle")
            self.text(x + w / 2, y + h / 2 + 13, sub, size=10.5, weight=500, color=t["muted_fg"], anchor="middle")
        else:
            self.text(x + w / 2, y + h / 2 + 4.5, title, size=12.5, weight=700, anchor="middle")

    # The hero: a tall pill in the primary colour with the mark and a name.
    def hero(self, x, y, w, h, lines):
        t = self.t
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w / 2}" fill="{t["primary"]}"/>')
        cx = x + w / 2
        my = y + 34
        self.add(f'<g fill="none" stroke="{t["primary_fg"]}" stroke-width="2" stroke-linecap="round">'
                 f'<circle cx="{cx}" cy="{my}" r="11"/><circle cx="{cx}" cy="{my}" r="5.5"/>'
                 f'<path d="M{cx} {my}l8 -8"/></g><circle cx="{cx}" cy="{my}" r="2" fill="{t["primary_fg"]}"/>')
        for i, line in enumerate(lines):
            self.text(cx, my + 34 + i * 15, line, size=12, weight=700, color=t["primary_fg"], anchor="middle")

    # A state pill, filled in a colour of its own.
    def pill(self, x, y, w, h, label, fill, color):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{fill}"/>')
        self.text(x + w / 2, y + h / 2 + 4.5, label, size=12.5, weight=700, color=color, anchor="middle")

    # A connector along points, with an arrowhead and an optional label at
    # the middle of a chosen segment (or at a point).
    def arrow(self, pts, label=None, at=None, dashed=False, head=True, color=None):
        t = self.t
        color = color or t["line"]
        d = " ".join(f"{'M' if i == 0 else 'L'}{x} {y}" for i, (x, y) in enumerate(pts))
        dash = ' stroke-dasharray="4 4"' if dashed else ""
        mk = f' marker-end="url(#head-{self.t["id"]})"' if head else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.5"{dash}{mk}/>')
        if label:
            if at is None:
                (x1, y1), (x2, y2) = pts[0], pts[-1] if len(pts) == 2 else pts[len(pts) // 2]
                at = ((x1 + x2) / 2, (y1 + y2) / 2)
            self.label(at[0], at[1], label)

    # A small label on a pill of the page's background, so it reads over a line.
    def label(self, x, y, s, size=10.5):
        t = self.t
        w = len(s) * size * 0.56 + 14
        self.add(f'<rect x="{x - w / 2}" y="{y - 9}" width="{w}" height="18" rx="9" fill="{t["bg"]}" stroke="{t["border"]}"/>')
        self.text(x, y + 3.5, s, size=size, weight=600, color=t["muted_fg"], anchor="middle")

    def svg(self):
        t = self.t
        head = (f'<defs><marker id="head-{t["id"]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                f'orient="auto-start-reverse"><path d="M0 0.5L9.5 5L0 9.5z" fill="{t["line"]}"/></marker></defs>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                + head + "".join(self.parts) + "</svg>")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# The provider marks, as the console draws them (cloud-logo.tsx), in a 16 box.
def _microsoft(x, y, t):
    s, g = 7.25, 1.5
    return (f'<g><rect x="{x}" y="{y}" width="{s}" height="{s}" fill="#f25022"/>'
            f'<rect x="{x + s + g}" y="{y}" width="{s}" height="{s}" fill="#7fba00"/>'
            f'<rect x="{x}" y="{y + s + g}" width="{s}" height="{s}" fill="#00a4ef"/>'
            f'<rect x="{x + s + g}" y="{y + s + g}" width="{s}" height="{s}" fill="#ffb900"/></g>')


def _aws(x, y, t):
    return (f'<g><text x="{x + 8}" y="{y + 9}" text-anchor="middle" font-family="{FONT}" font-size="9.5" font-weight="700" '
            f'letter-spacing="-0.3" fill="{t["fg"]}">aws</text>'
            f'<path d="M {x + 1.5} {y + 11.5} Q {x + 8} {y + 15.5} {x + 14} {y + 11.2}" fill="none" stroke="#ff9900" stroke-width="1.5" stroke-linecap="round"/>'
            f'<path d="M {x + 11.6} {y + 10.6} L {x + 14.6} {y + 10.9} L {x + 14} {y + 13.6}" fill="none" stroke="#ff9900" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></g>')


def _gcp(x, y, t):
    c = lambda d, s: f'<path d="{d}" fill="none" stroke="{s}" stroke-width="1.8" stroke-linecap="round"/>'
    return (f'<g transform="translate({x} {y})">' + c("M 4.6 12.5 H 11.6", "#34a853") + c("M 11.6 12.5 A 3 3 0 0 0 12.6 6.7", "#4285f4")
            + c("M 12.6 6.7 A 4.6 4.6 0 0 0 4.4 5.8", "#ea4335") + c("M 4.4 5.8 A 3.4 3.4 0 0 0 4.6 12.5", "#fbbc04") + "</g>")


def _databricks(x, y, t):
    layer = lambda top: f'<path d="M 2 {top + 2.5} L 8 {top} L 14 {top + 2.5} L 8 {top + 5} Z" fill="#ff3621"/>'
    return f'<g transform="translate({x} {y})">' + layer(1.5) + layer(5.5) + layer(9.5) + "</g>"


def _anthropic(x, y, t):
    return (f'<g transform="translate({x} {y}) scale({16 / 24})"><path d="M17.3 3.54h-3.67l6.7 16.92H24Zm-10.6 0L0 20.46h3.74l1.37-3.55h7l1.37 3.55h3.75L10.54 3.54Zm-.37 10.22 2.29-5.94 2.29 5.94Z" fill="#d97757" fill-rule="evenodd"/></g>')


def _snowflake(x, y, t):
    arms = "".join(f'<g transform="rotate({a})"><path d="M0 0 V-6.5"/><path d="M-2 -5 L0 -3.2 L2 -5"/></g>' for a in range(0, 360, 60))
    return f'<g transform="translate({x + 8} {y + 8})" stroke="#29b5e8" stroke-width="1.6" stroke-linecap="round" fill="none">{arms}</g>'


LOGOS = dict(microsoft=_microsoft, aws=_aws, gcp=_gcp, databricks=_databricks, anthropic=_anthropic, snowflake=_snowflake)


# ---------------------------------------------------------------- diagrams

def system(c):
    """The product in one picture: the clouds it reads, the workloads it
    fronts, OpenController in the middle, and what it gives you."""
    t = c.t
    # Left: the clouds, and the workloads.
    c.group(0, 0, 176, 214, "Your clouds and platforms")
    clouds = [("AWS", "aws"), ("Microsoft", "microsoft"), ("Google Cloud", "gcp"), ("Databricks", "databricks"),
              ("Anthropic", "anthropic"), ("Snowflake", "snowflake")]
    for i, (name, logo) in enumerate(clouds):
        c.chip(12, 30 + i * 30, 152, 24, name, logo=logo)
    c.group(0, 230, 176, 92, "Your workloads")
    c.chip(12, 260, 152, 24, "Applications", strong=True)
    c.chip(12, 290, 152, 24, "Agents", strong=True)

    # Centre: the hero.
    c.hero(316, 44, 72, 236, ["Open", "Controller"])

    # Left arrows, labelled in the gap.
    c.arrow([(176, 96), (316, 126)], label="scans read", at=(246, 96))
    c.arrow([(316, 170), (176, 140)], label="block, share, delete", at=(246, 172))
    c.arrow([(176, 276), (316, 236)], label="calls and traces", at=(246, 270))

    # Right: what you get, in three groups.
    gx, gw, cw = 420, 300, 136
    c.group(gx, 0, gw, 96, "Discover and govern")
    c.chip(gx + 12, 30, cw, 24, "Inventory and map")
    c.chip(gx + 20 + cw, 30, cw, 24, "Shadow AI")
    c.chip(gx + 12, 60, cw, 24, "Registry, approvals")
    c.chip(gx + 20 + cw, 60, cw, 24, "Control actions")
    c.group(gx, 112, gw, 96, "Run")
    c.chip(gx + 12, 142, cw, 24, "LLM gateway")
    c.chip(gx + 20 + cw, 142, cw, 24, "Virtual keys, teams")
    c.chip(gx + 12, 172, cw, 24, "Guardrails")
    c.chip(gx + 20 + cw, 172, cw, 24, "Model providers")
    c.group(gx, 224, gw, 98, "Watch and improve")
    c.chip(gx + 12, 254, cw, 24, "Traces and cost")
    c.chip(gx + 20 + cw, 254, cw, 24, "Findings, posture")
    c.chip(gx + 12, 284, cw, 24, "Evals")
    c.chip(gx + 20 + cw, 284, cw, 24, "Fine-tuning")

    # Hero to the groups: one elbow each.
    c.arrow([(388, 110), (404, 110), (404, 48), (gx, 48)])
    c.arrow([(388, 160), (gx, 160)])
    c.arrow([(388, 214), (404, 214), (404, 272), (gx, 272)])


def flow(c):
    """Discover, govern, control, observe, evaluate: one agent, in order."""
    t = c.t
    steps = [("Discover", "scan every cloud"), ("Govern", "register, approve, policy"),
             ("Control", "block, share, delete"), ("Observe", "traces, cost, issues"), ("Evaluate", "score the traces")]
    w, h, gap, y = 124, 56, 25, 36
    for i, (title, sub) in enumerate(steps):
        x = i * (w + gap)
        c.node(x, y, w, h, title, sub, accent=t["primary"] if i in (0, 4) else None)
        if i < 4:
            c.arrow([(x + w, y + h / 2), (x + w + gap, y + h / 2)])
    # What each step hands the next, under the arrows.
    hands = ["assets and owners", "who is allowed", "what still runs", "traces"]
    for i, s in enumerate(hands):
        c.text(i * (w + gap) + w + gap / 2, y + h + 16, s, size=10, weight=600, color=t["muted_fg"], anchor="middle")
    # Scores go back to the owner: a return line under the row.
    c.arrow([(4 * (w + gap) + w / 2, y + h), (4 * (w + gap) + w / 2, y + h + 50), (w + gap + w / 2, y + h + 50), (w + gap + w / 2, y + h + 2)],
            label="scores, back to the owner", at=(2.5 * (w + gap) + w / 2, y + h + 50), dashed=True)
    # The credentials each step needs.
    c.label(w / 2, 14, "read credential")
    c.label(2 * (w + gap) + w / 2, 14, "control credential")


def states(c):
    """Where an asset stands with the organisation, and how it moves."""
    t = c.t
    y, h = 60, 34
    c.pill(0, y, 112, h, "Shadow", t["alt"], "#ffffff")
    c.pill(214, y, 166, h, "Awaiting approval", t["muted"], t["fg"])
    c.pill(484, y, 130, h, "Registered", t["primary"], t["primary_fg"])
    c.arrow([(112, y + h / 2), (214, y + h / 2)], label="register", at=(163, y + h / 2 - 20))
    c.arrow([(380, y + h / 2), (484, y + h / 2)], label="approve", at=(432, y + h / 2 - 20))
    # The ways back to shadow.
    c.arrow([(297, y + h), (297, y + h + 52), (56, y + h + 52), (56, y + h)], label="reject or withdraw", at=(176, y + h + 52))
    c.arrow([(549, y + h), (549, y + h + 86), (56, y + h + 86), (56, y + h + 2)], label="revoke", at=(302, y + h + 86), head=True)
    c.text(0, 22, "Discovered on a connected platform", size=11, weight=600, color=t["muted_fg"])
    c.arrow([(56, 28), (56, y)], head=True)
    c.text(614 + 10, y + h / 2 + 4, "with an owner,", size=10.5, weight=600, color=t["muted_fg"])
    c.text(614 + 10, y + h / 2 + 18, "in the registry", size=10.5, weight=600, color=t["muted_fg"])


def credentials(c):
    """The two credentials a connection holds, and what each may do."""
    t = c.t
    c.group(0, 0, 250, 176, "OpenController")
    c.node(14, 32, 222, 50, "Discovery, Verify, Spend", "lists and describes")
    c.node(14, 100, 222, 50, "Control actions", "share, block, publish, delete")
    c.group(470, 0, 250, 176, "The account")
    for i, s in enumerate(["Agents", "Models and tools", "Identities and keys", "Sharing and publishing"]):
        c.chip(484, 30 + i * 32, 222, 24, s)
    c.arrow([(236, 57), (470, 57)], label="read credential, required", at=(353, 40))
    c.text(353, 72, "reads, changes nothing", size=10, weight=600, color=t["muted_fg"], anchor="middle")
    c.arrow([(236, 125), (470, 125)], label="control credential, optional", at=(353, 108))
    c.text(353, 140, "off until you grant it", size=10, weight=600, color=t["muted_fg"], anchor="middle")
    c.node(60, 200, 130, 40, "Secrets manager")
    c.arrow([(125, 200), (125, 150)], dashed=True, head=False)
    c.text(204, 224, "holds both credentials; never returned, never logged", size=10, weight=600, color=t["muted_fg"], anchor="start")


def gateway(c):
    """A model call through the gateway: key, rules, provider, back."""
    t = c.t
    c.node(0, 92, 140, 56, "Your application", "any OpenAI SDK")
    c.hero(214, 30, 72, 180, ["LLM", "gateway"])
    c.arrow([(140, 112), (214, 112)], label="virtual key", at=(177, 94))
    c.arrow([(214, 132), (140, 132)], label="answer", at=(177, 150))
    c.node(360, 92, 150, 56, "Content rules", "your guardrails")
    c.arrow([(286, 112), (360, 112)], label="prompt", at=(323, 94))
    c.arrow([(360, 132), (286, 132)], label="checked answer", at=(323, 150))
    c.group(560, 0, 160, 240, "Model providers")
    for i, s in enumerate(["OpenAI", "Anthropic", "AWS Bedrock", "Azure OpenAI", "Google Vertex AI", "OpenAI-compatible"]):
        c.chip(572, 30 + i * 32, 136, 24, s)
    c.arrow([(510, 120), (560, 120)])
    c.node(180, 232, 140, 40, "Logs and spend")
    c.node(360, 232, 150, 40, "Guardrail violations")
    c.arrow([(250, 210), (250, 232)], dashed=True)
    c.arrow([(435, 148), (435, 232)], dashed=True)
    c.text(0, 26, "The key decides the providers, models, budget and rate limits.", size=10.5, weight=600, color=t["muted_fg"])


def traces(c):
    """How a trace gets from an agent to the pages that show it."""
    t = c.t
    c.node(0, 30, 130, 56, "Your agent", "with an OTel SDK")
    c.node(260, 30, 170, 56, "OpenTelemetry Collector", "in your cell")
    c.arrow([(130, 58), (260, 58)], label="OTLP over HTTP", at=(195, 40))
    c.text(195, 78, "project key in a header", size=10, weight=600, color=t["muted_fg"], anchor="middle")
    # ClickHouse as a cylinder.
    x, y, w, h = 490, 22, 120, 72
    c.add(f'<path d="M{x} {y + 10} a{w / 2} 10 0 0 1 {w} 0 v{h - 20} a{w / 2} 10 0 0 1 -{w} 0 z" fill="{t["bg"]}" stroke="{t["border_strong"]}"/>')
    c.add(f'<ellipse cx="{x + w / 2}" cy="{y + 10}" rx="{w / 2}" ry="10" fill="{t["bg"]}" stroke="{t["border_strong"]}"/>')
    c.text(x + w / 2, y + 44, "ClickHouse", size=12.5, weight=700, anchor="middle")
    c.text(x + w / 2, y + 58, "the trace store", size=10.5, weight=500, color=t["muted_fg"], anchor="middle")
    c.arrow([(430, 58), (490, 58)], label="writes", at=(460, 40))
    c.node(260, 140, 170, 44, "Observability pages", "traces, issues, cost")
    c.node(490, 140, 120, 44, "Evals service", "reads records")
    c.arrow([(560, 94), (560, 140)])
    c.arrow([(530, 94), (530, 115), (345, 115), (345, 140)], label="read-only user", at=(437, 115))


def evals(c):
    """The judging loop: records in, a question to a model, scores out."""
    t = c.t
    x, y, w, h = 0, 78, 120, 72
    c.add(f'<path d="M{x} {y + 10} a{w / 2} 10 0 0 1 {w} 0 v{h - 20} a{w / 2} 10 0 0 1 -{w} 0 z" fill="{t["bg"]}" stroke="{t["border_strong"]}"/>')
    c.add(f'<ellipse cx="{x + w / 2}" cy="{y + 10}" rx="{w / 2}" ry="10" fill="{t["bg"]}" stroke="{t["border_strong"]}"/>')
    c.text(x + w / 2, y + 44, "Trace store", size=12.5, weight=700, anchor="middle")
    c.text(x + w / 2, y + 58, "spans and runs", size=10, weight=500, color=t["muted_fg"], anchor="middle")
    c.hero(214, 24, 72, 180, ["Evals", "service"])
    c.arrow([(120, 114), (214, 114)], label="records", at=(167, 96))
    c.node(360, 24, 150, 56, "Judge model", "answers each question")
    c.arrow([(286, 60), (360, 60)], label="question", at=(323, 42))
    c.arrow([(360, 72), (286, 72)], label="answer", at=(323, 92))
    c.node(360, 150, 150, 44, "Scores", "per record, over time")
    c.arrow([(286, 172), (360, 172)])
    c.group(560, 100, 160, 140, "Where scores go")
    for i, s in enumerate(["Scores page", "Findings (OBS-2)", "Monitors and alerts"]):
        c.chip(572, 130 + i * 32, 136, 24, s)
    c.arrow([(510, 172), (560, 172)])


DIAGRAMS = {
    "system": (720, 322, system),
    "flow": (720, 160, flow),
    "states": (720, 190, states),
    "credentials": (720, 250, credentials),
    "gateway": (720, 276, gateway),
    "traces": (720, 190, traces),
    "evals": (720, 244, evals),
}


def render(name, w, h, draw):
    for theme, tokens in THEMES.items():
        t = dict(tokens, id=theme)
        c = Canvas(w, h, t)
        draw(c)
        html = (f'<!doctype html><meta charset="utf-8">'
                f'<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">'
                f'<style>html,body{{margin:0;background:transparent}}svg{{display:block}}</style>'
                f'<body>{c.svg()}</body>')
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(html)
            path = f.name
        out = os.path.join(OUT, f"{name}-{theme}.png")
        subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=2",
                        "--default-background-color=00000000", f"--window-size={w},{h}", "--virtual-time-budget=8000",
                        f"--screenshot={out}", f"file://{path}"], check=True, capture_output=True)
        os.unlink(path)
        print(f"{out} ({w}x{h} @2x)")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[1:] or list(DIAGRAMS)
    for n in names:
        w, h, draw = DIAGRAMS[n]
        render(n, w, h, draw)
