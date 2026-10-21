// The page's own behaviour, run by Mintlify on every page after it is interactive.
//
// 1. The section's tone follows you: the path sets data-tone on <html>, and the stylesheet
//    colours the current sidebar row, the table of contents and the reading line from it.
// 2. A "Who can do this" paragraph becomes a permission strip, with the permissions as keys.
// 3. HTTP methods in the API tables and lists become method tags.
// 4. [ and ] move to the previous and next page; the footer says so.
// 5. A reading line under the navbar shows how far down the page you are.
(function () {
  "use strict";
  if (window.__ocUi) return;
  window.__ocUi = true;

  var TONES = [
    ["/discover", "discover"], ["/govern/respond", "control"], ["/govern/control-actions", "control"],
    ["/govern", "govern"], ["/runtime", "runtime"], ["/posture", "posture"], ["/monitor", "observe"],
    ["/improve", "observe"], ["/connect", "runtime"], ["/assistant", "runtime"],
  ];
  var METHODS = /^(GET|POST|PUT|PATCH|DELETE)\b/;

  function tone(path) {
    for (var i = 0; i < TONES.length; i++) if (path.indexOf(TONES[i][0]) === 0) return TONES[i][1];
    return "";
  }

  function setTone() {
    var t = tone(location.pathname);
    if (t) document.documentElement.setAttribute("data-tone", t);
    else document.documentElement.removeAttribute("data-tone");
  }

  // "Who can do this: `assets:read` to read…" → a strip with a key mark, the label, and the rest.
  function permissionStrips(root) {
    // Mintlify renders a paragraph as <p>, or as <span data-as="p"> inside a custom block.
    var ps = root.querySelectorAll('p:not(.oc-done), span[data-as="p"]:not(.oc-done)');
    for (var i = 0; i < ps.length; i++) {
      var p = ps[i];
      var first = p.firstElementChild;
      var text = (p.textContent || "").replace(/\s+/g, " ").trim();
      if (!/^Who can do this:?/i.test(text)) continue;
      p.classList.add("oc-done");
      if (first && first.tagName === "STRONG" && /^Who can do this/i.test(first.textContent)) p.removeChild(first);
      // Drop the leading label and colon from a plain-text start.
      if (p.firstChild && p.firstChild.nodeType === 3) p.firstChild.nodeValue = p.firstChild.nodeValue.replace(/^\s*Who can do this:?\s*/i, "");
      var strip = document.createElement("div");
      strip.className = "oc-who";
      strip.innerHTML =
        '<span class="oc-who-label"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.6 21.4l10.5-10.5"/><circle cx="16.5" cy="7.5" r="4.5"/><path d="M7.5 16.5l2 2M10.5 13.5l2 2"/></svg>Who can do this</span>';
      var body = document.createElement("span");
      body.className = "oc-who-body";
      while (p.firstChild) body.appendChild(p.firstChild);
      strip.appendChild(body);
      p.parentNode.replaceChild(strip, p);
    }
  }

  // `GET /v1/assets` → the method as a tag, the path as code.
  function methodTags(root) {
    var codes = root.querySelectorAll("code:not(.oc-done)");
    for (var i = 0; i < codes.length; i++) {
      var c = codes[i];
      var m = METHODS.exec(c.textContent || "");
      if (!m || c.closest("pre") || c.closest("#navbar, #sidebar")) continue;
      c.classList.add("oc-done");
      if (c.textContent.trim() === m[1]) { c.classList.add("oc-method", "oc-method-" + m[1].toLowerCase()); continue; }
      var tag = document.createElement("span");
      tag.className = "oc-method oc-method-" + m[1].toLowerCase();
      tag.textContent = m[1];
      c.textContent = c.textContent.slice(m[1].length).replace(/^\s+/, "");
      c.classList.add("oc-path");
      c.parentNode.insertBefore(tag, c);
    }
  }

  function pageLinks() {
    var nav = document.querySelector("#content-container nav.grid");
    if (!nav) return {};
    var links = nav.querySelectorAll("a[href]");
    var out = {};
    for (var i = 0; i < links.length; i++) {
      var t = links[i].textContent || "";
      if (/Previous/.test(t)) out.prev = links[i];
      if (/Next/.test(t)) out.next = links[i];
    }
    if (!nav.querySelector(".oc-keys")) {
      var hint = document.createElement("p");
      hint.className = "oc-keys";
      hint.innerHTML = "<kbd>[</kbd> previous page <span>·</span> <kbd>]</kbd> next page";
      nav.appendChild(hint);
    }
    return out;
  }

  function onKey(e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var el = document.activeElement;
    if (el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.isContentEditable)) return;
    if (e.key !== "[" && e.key !== "]") return;
    var links = pageLinks();
    var a = e.key === "[" ? links.prev : links.next;
    if (a) { e.preventDefault(); a.click(); }
  }

  var line;
  function readingLine() {
    if (!line) {
      line = document.createElement("div");
      line.className = "oc-reading";
      line.setAttribute("aria-hidden", "true");
      document.body.appendChild(line);
    }
    var doc = document.documentElement;
    var max = doc.scrollHeight - doc.clientHeight;
    var p = max > 0 ? Math.min(1, doc.scrollTop / max) : 0;
    line.style.transform = "scaleX(" + p.toFixed(4) + ")";
  }

  var pending;
  function decorate() {
    clearTimeout(pending);
    pending = setTimeout(function () {
      setTone();
      var root = document.getElementById("content-container");
      if (!root) return;
      permissionStrips(root);
      methodTags(root);
      pageLinks();
      readingLine();
    }, 60);
  }

  document.addEventListener("keydown", onKey);
  window.addEventListener("scroll", readingLine, { passive: true });
  window.addEventListener("resize", readingLine);
  new MutationObserver(decorate).observe(document.body, { childList: true, subtree: true });
  decorate();
})();

// ---- The estate reader ------------------------------------------------------------------
// 6. An answer strip under the title: where the page lives in the console, and who can act.
// 7. A diagram's nodes light the prose that names them.
// 8. The home page's walkthrough plays as a stepper.
(function () {
  "use strict";
  if (window.__ocEstate) return;
  window.__ocEstate = true;

  // Where each page lives in the console: the sidebar section and the page.
  var CONSOLE = {
    "/discover/overview": ["Overview"], "/discover/inventory": ["Discover", "AI Inventory"], "/discover/map": ["Discover", "AI Inventory", "Map"],
    "/discover/shadow-ai": ["Discover", "Shadow AI"], "/discover/people": ["Discover", "People"], "/discover/spend": ["Spend"],
    "/govern/registry": ["Govern", "Registry"], "/govern/approvals": ["Govern", "Approvals"], "/govern/policies": ["Govern", "Policies"],
    "/govern/audit-log": ["Settings", "Audit log"], "/govern/respond": ["Discover", "Shadow AI"], "/govern/control-actions": ["Discover", "AI Inventory", "an asset's Actions"],
    "/monitor/observability": ["Monitor", "Observability"], "/monitor/send-traces": ["Monitor", "Observability", "Setup"], "/monitor/traces-and-issues": ["Monitor", "Observability", "Traces"],
    "/monitor/cost": ["Monitor", "Observability", "Cost"], "/monitor/evals": ["Monitor", "Evals"], "/monitor/evaluators-and-tasks": ["Monitor", "Evals", "Evaluators"],
    "/monitor/monitors-and-datasets": ["Monitor", "Evals", "Monitors"], "/runtime/llm-gateway": ["Runtime", "LLM Gateway"], "/runtime/virtual-keys": ["Runtime", "LLM Gateway", "Virtual keys"],
    "/runtime/teams-and-customers": ["Runtime", "LLM Gateway", "Teams & customers"], "/runtime/gateway-logs": ["Runtime", "LLM Gateway", "Logs"], "/runtime/guardrails": ["Runtime", "Guardrails"],
    "/runtime/guardrail-checks": ["Runtime", "Guardrails", "Checks"], "/runtime/guardrail-violations": ["Runtime", "Guardrail Violations"], "/runtime/guardrails-api": ["Runtime", "Guardrails"],
    "/posture/findings": ["Posture", "Findings"], "/posture/security-policies": ["Posture", "Security policies"], "/posture/frameworks": ["Posture", "Findings", "Frameworks"],
    "/improve/fine-tuning": ["Improve", "Fine-tuning"], "/assistant/ask-ctrl": ["Ask Ctrl"], "/connect/overview": ["Integrations"], "/connect/aws": ["Integrations", "AWS"],
    "/connect/microsoft": ["Integrations", "Microsoft"], "/connect/google-cloud": ["Integrations", "Google Cloud"], "/connect/databricks": ["Integrations", "Databricks"],
    "/connect/anthropic": ["Integrations", "Anthropic"], "/connect/snowflake": ["Integrations", "Snowflake"], "/connect/scans": ["Integrations", "Scans"],
    "/get-started/quickstart": ["Integrations"], "/get-started/modules": ["Overview"],
  };
  var ROLES = [["admin", /\badmin(istrator)?s?\b/i], ["operator", /\boperators?\b/i], ["viewer", /\bviewers?\b/i]];

  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function answerStrip() {
    var header = document.querySelector("#content-area #header");
    if (!header || header.parentNode.querySelector(".oc-answer")) return;
    var place = CONSOLE[location.pathname.replace(/\/$/, "")];
    var who = document.querySelector("#content-area .oc-who");
    var inAtlas = window.__ocAtlas && window.__ocAtlas.pages[location.pathname.replace(/\/$/, "")];
    if (!place && !who && !inAtlas) return;
    var strip = document.createElement("div");
    strip.className = "oc-answer";
    var html = "";
    if (place) {
      var mark = document.querySelector('#navigation-items a[aria-current="page"] svg');
      html += '<div class="oc-answer-cell"><span class="oc-answer-k">In the console</span><span class="oc-answer-v oc-crumb">' +
        (mark ? mark.outerHTML : "") + place.map(function (p) { return "<span>" + esc(p) + "</span>"; }).join('<i aria-hidden="true">›</i>') + "</span></div>";
    }
    if (who) {
      var text = who.textContent || "";
      var roles = ROLES.filter(function (r) { return r[1].test(text); }).map(function (r) { return r[0]; });
      if (roles.length) {
        html += '<div class="oc-answer-cell"><span class="oc-answer-k">Who can act</span><span class="oc-answer-v">' +
          roles.map(function (r) { return '<span class="oc-role oc-role-' + r + '">' + r + "</span>"; }).join("") + "</span></div>";
      }
    }
    strip.innerHTML = html;
    header.parentNode.insertBefore(strip, header.nextSibling);
  }

  // Hovering a node lights every paragraph, row and item that names it.
  var lit = [];
  function unlight() { lit.forEach(function (e) { e.classList.remove("oc-lit"); }); lit = []; }
  var STOP = /^(your|the|a|an|with|in|of|and|or|on|to|service|pages|page|store)$/i;
  function light(name) {
    unlight();
    var words = name.split(/\s+/).filter(function (w) { return w && !STOP.test(w); });
    var key = words.length ? words[words.length - 1] : name;
    var re = new RegExp("\\b" + key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "s?\\b", "i");
    var blocks = document.querySelectorAll("#content-area p, #content-area span[data-as='p'], #content-area li, #content-area td, #content-area .oc-who");
    for (var i = 0; i < blocks.length; i++) {
      var b = blocks[i];
      if (b.closest(".oc-diagram") || b.querySelector("p, li")) continue;
      if (re.test(b.textContent || "")) { b.classList.add("oc-lit"); lit.push(b); }
    }
  }
  function bindNodes() {
    var nodes = document.querySelectorAll(".oc-diagram .oc-node:not(.oc-bound)");
    for (var i = 0; i < nodes.length; i++) (function (n) {
      n.classList.add("oc-bound");
      var name = n.getAttribute("data-name") || "";
      n.addEventListener("mouseenter", function () { light(name); n.closest(".oc-diagram").classList.add("oc-focus"); });
      n.addEventListener("focus", function () { light(name); n.closest(".oc-diagram").classList.add("oc-focus"); });
      n.addEventListener("mouseleave", function () { unlight(); n.closest(".oc-diagram").classList.remove("oc-focus"); });
      n.addEventListener("blur", function () { unlight(); n.closest(".oc-diagram").classList.remove("oc-focus"); });
    })(nodes[i]);
  }

  // The walkthrough: a play control steps the tabs every few seconds, and a line under the
  // active tab shows the time left. Any touch stops it; a hidden tab pauses it.
  var timer, playing = false, STEP = 4200;
  function tabs() { return Array.prototype.slice.call(document.querySelectorAll(".oc-panel [role='tablist'] [role='tab']")); }
  function current() { return tabs().findIndex(function (t) { return t.getAttribute("aria-selected") === "true"; }); }
  function go(i) { var ts = tabs(); if (!ts.length) return; ts[(i + ts.length) % ts.length].click(); }
  function tick() {
    if (!playing) return;
    var panel = document.querySelector(".oc-panel");
    if (panel) { panel.classList.remove("oc-playing"); void panel.offsetWidth; panel.classList.add("oc-playing"); }
    timer = setTimeout(function () { go(current() + 1); tick(); }, STEP);
  }
  function setPlaying(on) {
    playing = on;
    clearTimeout(timer);
    var panel = document.querySelector(".oc-panel");
    var btn = panel && panel.querySelector(".oc-play");
    if (btn) { btn.setAttribute("aria-pressed", on ? "true" : "false"); btn.querySelector("span").textContent = on ? "Pause" : "Play"; btn.classList.toggle("is-on", on); }
    if (panel) panel.classList.toggle("oc-playing", on);
    if (on) tick();
  }
  function stepper() {
    var panel = document.querySelector(".oc-panel");
    if (!panel || panel.querySelector(".oc-play")) return;
    var head = panel.querySelector(".oc-panel-head");
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "oc-play";
    btn.setAttribute("aria-pressed", "false");
    btn.innerHTML = '<svg viewBox="0 0 24 24" width="12" height="12" aria-hidden="true"><path class="oc-play-i" d="M7 4.5v15l12-7.5z" fill="currentColor"/><path class="oc-pause-i" d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z" fill="currentColor"/></svg><span>Play</span>';
    btn.addEventListener("click", function () { setPlaying(!playing); });
    head.appendChild(btn);
    panel.addEventListener("pointerdown", function (e) { if (!e.target.closest(".oc-play")) setPlaying(false); });
    document.addEventListener("visibilitychange", function () { if (document.hidden) setPlaying(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      if (!e.target.closest || !e.target.closest(".oc-panel")) return;
      setPlaying(false); go(current() + (e.key === "ArrowRight" ? 1 : -1)); e.preventDefault();
    });
  }

  // The controls a page helps evidence, from atlas.js (generated from the Frameworks page):
  // one chip per framework with its count, the codes in the chip's title.
  function controlsCell() {
    var atlas = window.__ocAtlas;
    var strip = document.querySelector("#content-area .oc-answer");
    if (!atlas || !strip || strip.querySelector(".oc-answer-fw")) return;
    var mine = atlas.pages[location.pathname.replace(/\/$/, "")];
    if (!mine) return;
    var chips = atlas.frameworks.filter(function (f) { return mine[f.id] && mine[f.id].length; }).map(function (f) {
      return '<a class="oc-fw" href="/posture/frameworks" title="' + esc(mine[f.id].join(", ")) + '">' + esc(f.label) + " <b>" + mine[f.id].length + "</b></a>";
    });
    if (!chips.length) return;
    var cell = document.createElement("div");
    cell.className = "oc-answer-cell oc-answer-fw";
    cell.innerHTML = '<span class="oc-answer-k">Framework controls</span><span class="oc-answer-v">' + chips.join("") + "</span>";
    strip.appendChild(cell);
  }

  // The atlas's framework picker: one column lit, the rest recede. Event delegation, so it
  // survives Mintlify re-rendering the page.
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-fw-pick]");
    if (!b) return;
    var atlas = b.closest(".oc-atlas");
    if (!atlas) return;
    var id = b.getAttribute("data-fw-pick");
    var same = atlas.getAttribute("data-fw") === id;
    var next = same ? "all" : id;
    atlas.setAttribute("data-fw", next);
    Array.prototype.forEach.call(atlas.querySelectorAll("[data-fw-pick]"), function (x) {
      x.setAttribute("aria-pressed", x.getAttribute("data-fw-pick") === next ? "true" : "false");
    });
  });

  var pending;
  function run() {
    clearTimeout(pending);
    pending = setTimeout(function () { answerStrip(); controlsCell(); bindNodes(); stepper(); }, 120);
  }
  new MutationObserver(run).observe(document.body, { childList: true, subtree: true });
  run();
})();
