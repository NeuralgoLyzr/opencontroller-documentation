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
