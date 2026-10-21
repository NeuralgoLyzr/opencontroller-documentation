// Ask the docs: a chat panel on every page that answers from these pages
// through OpenController's own LLM gateway. Mintlify runs this file after
// the page is interactive. The page sends the question and the current
// page's Markdown; the gateway adds the stored system prompt, applies the
// key's budget, rate limit and content rules, and streams the answer.
//
// The key below is a browser key: public by design, allowed one model,
// capped by a budget and a rate limit. scripts/gateway/setup.sh creates it
// and fills this block in.
const CONFIG = {
  gateway: "",   // e.g. https://gateway.opencontroller.sh
  key: "",       // the browser virtual key
  promptId: "",  // the prompt repository id of the system prompt
  model: "",     // e.g. anthropic/claude-haiku-5-5
  maxTokens: 700,
};

(function () {
  if (!CONFIG.gateway || !CONFIG.key) return;

  const STORE = "oc-docs-assistant";
  const PAGE_CHARS = 14000;
  const INDEX_CHARS = 6000;
  let open = false;
  let busy = false;
  let turns = load();

  // The icon is the console's assistant mark: a speech bubble with a question mark.
  const icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>';

  const button = el("button", "oc-ask-button", icon + "<span>Ask the docs</span>");
  button.setAttribute("aria-label", "Ask the docs");
  const panel = el("section", "oc-ask-panel", "");
  panel.setAttribute("aria-label", "Ask the docs");
  panel.hidden = true;
  panel.innerHTML =
    '<header><h2>Ask the docs</h2><button class="oc-ask-close" aria-label="Close">&times;</button></header>' +
    '<div class="oc-ask-messages" role="log" aria-live="polite"></div>' +
    '<form class="oc-ask-form"><textarea rows="1" placeholder="How do I block an agent?" aria-label="Your question"></textarea>' +
    '<button type="submit" aria-label="Send">&rarr;</button></form>' +
    '<footer>Answers come from these pages. Check the page before you act.</footer>';
  document.body.append(button, panel);

  const messages = panel.querySelector(".oc-ask-messages");
  const form = panel.querySelector("form");
  const input = panel.querySelector("textarea");

  button.addEventListener("click", () => toggle(!open));
  panel.querySelector(".oc-ask-close").addEventListener("click", () => toggle(false));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && open) toggle(false); });
  form.addEventListener("submit", (e) => { e.preventDefault(); ask(); });
  input.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(); } });
  input.addEventListener("input", () => { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 120) + "px"; });

  render();

  function toggle(to) {
    open = to;
    panel.hidden = !open;
    button.classList.toggle("is-open", open);
    if (open) input.focus();
  }

  async function ask() {
    const question = input.value.trim();
    if (!question || busy) return;
    busy = true;
    input.value = "";
    input.style.height = "auto";
    turns.push({ role: "user", content: question });
    const reply = { role: "assistant", content: "" };
    turns.push(reply);
    render();
    try {
      const context = await pageContext();
      await stream(context, reply);
    } catch (err) {
      reply.content = reply.content || explain(err);
      reply.error = true;
    }
    busy = false;
    save();
    render();
  }

  // The current page as Markdown, and the site's index, so the answer is
  // grounded in what the reader is looking at and can point elsewhere.
  async function pageContext() {
    const path = location.pathname.replace(/\/$/, "") || "/index";
    const [page, index] = await Promise.all([
      fetch(path + ".md").then((r) => (r.ok ? r.text() : "")).catch(() => ""),
      cached("index", () => fetch("/llms.txt").then((r) => (r.ok ? r.text() : "")).catch(() => "")),
    ]);
    return (
      "The reader is on " + location.pathname + ".\n\n" +
      "## Current page\n\n" + page.slice(0, PAGE_CHARS) + "\n\n" +
      "## Site index\n\n" + index.slice(0, INDEX_CHARS)
    );
  }

  async function stream(context, reply) {
    const history = turns.slice(-11, -1).map((t) => ({ role: t.role, content: t.content }));
    const res = await fetch(CONFIG.gateway + "/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-bf-vk": CONFIG.key,
        "x-bf-prompt-id": CONFIG.promptId,
      },
      body: JSON.stringify({
        model: CONFIG.model,
        stream: true,
        max_tokens: CONFIG.maxTokens,
        messages: [{ role: "system", content: context }, ...history],
      }),
    });
    if (!res.ok) throw new Error(String(res.status));
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();
      for (const line of lines) {
        if (!line.startsWith("data:")) continue;
        const data = line.slice(5).trim();
        if (data === "[DONE]") return;
        try {
          const delta = JSON.parse(data).choices?.[0]?.delta?.content;
          if (delta) { reply.content += delta; render(); }
        } catch (_) { /* a partial chunk; the next line completes it */ }
      }
    }
  }

  function explain(err) {
    switch (err.message) {
      case "402": return "The assistant's budget for today is used up. Try again tomorrow, or search the pages.";
      case "429": return "Too many questions at once. Try again in a minute.";
      case "446": return "That question was blocked by a content rule.";
      default: return "The assistant could not answer. Search the pages instead.";
    }
  }

  function render() {
    messages.innerHTML = turns.length
      ? turns.map((t) => '<div class="oc-ask-turn is-' + t.role + (t.error ? " is-error" : "") + '">' + markdown(t.content || (busy ? "…" : "")) + "</div>").join("")
      : '<p class="oc-ask-empty">Ask how something works, or where a setting is. The answer comes from these pages, with links.</p>';
    messages.scrollTop = messages.scrollHeight;
  }

  // Enough Markdown for an answer: paragraphs, bullets, code, links.
  function markdown(text) {
    const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    const inline = (s) =>
      esc(s)
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
        .replace(/\[([^\]]+)\]\((\/[^)\s]+|https?:[^)\s]+)\)/g, '<a href="$2">$1</a>');
    const blocks = text.split(/\n{2,}/);
    return blocks
      .map((b) => {
        if (/^```/.test(b)) return "<pre><code>" + esc(b.replace(/^```\w*\n?|```$/g, "")) + "</code></pre>";
        if (/^(\s*[-*] .*\n?)+$/.test(b)) return "<ul>" + b.trim().split("\n").map((l) => "<li>" + inline(l.replace(/^\s*[-*] /, "")) + "</li>").join("") + "</ul>";
        if (/^(\s*\d+\. .*\n?)+$/.test(b)) return "<ol>" + b.trim().split("\n").map((l) => "<li>" + inline(l.replace(/^\s*\d+\. /, "")) + "</li>").join("") + "</ol>";
        return "<p>" + inline(b).replace(/\n/g, "<br>") + "</p>";
      })
      .join("");
  }

  function el(tag, cls, html) { const n = document.createElement(tag); n.className = cls; n.innerHTML = html; return n; }
  function load() { try { return JSON.parse(sessionStorage.getItem(STORE)) || []; } catch (_) { return []; } }
  function save() { try { sessionStorage.setItem(STORE, JSON.stringify(turns.slice(-20))); } catch (_) { /* storage off */ } }
  const memo = {};
  function cached(k, f) { return (memo[k] ||= f()); }
})();
