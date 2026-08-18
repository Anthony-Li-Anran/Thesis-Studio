"""Chat message renderer for DESIGNING phase.

Enhanced markdown rendering with code highlighting, copy buttons, and polished typography.
"""

from __future__ import annotations

import re

from nicegui import ui

AGENT_COLORS = {"researcher": "#2563eb", "debater": "#7c3aed", "reviewer": "#db2777"}
AGENT_LABELS = {"researcher": "Researcher", "debater": "Debater", "reviewer": "Reviewer"}
AGENT_LIST = ["researcher", "debater", "reviewer"]

_MD_CSS = """<style>
/* === Markdown Typography === */
.ts-chat-md {
  overflow-wrap:anywhere; word-break:break-word; hyphens:auto;
  line-height: 1.6; color: var(--text-nav-primary);
}
.ts-chat-md h1, .ts-chat-md h2, .ts-chat-md h3, .ts-chat-md h4 {
  font-weight: 600; margin: 0.75em 0 0.3em; line-height: 1.3;
}
.ts-chat-md h1 { font-size: 1.1rem; border-bottom: 1px solid var(--border-outline); padding-bottom: 0.2em; }
.ts-chat-md h2 { font-size: 1rem; }
.ts-chat-md h3 { font-size: 0.9rem; }
.ts-chat-md h4 { font-size: 0.85rem; color: var(--text-nav-secondary); }
.ts-chat-md p { margin: 0.3em 0; line-height: 1.6; max-width:100%; overflow-wrap:anywhere; }
.ts-chat-md ul, .ts-chat-md ol { margin: 0.3em 0; padding-left: 1.5em; }
.ts-chat-md li { margin: 0.15em 0; overflow-wrap:anywhere; }
.ts-chat-md li > p { margin: 0; }
.ts-chat-md a { color: #60a5fa; text-decoration: underline; text-underline-offset: 2px; }
.ts-chat-md a:hover { color: #93c5fd; }
.ts-chat-md strong { font-weight: 600; color: var(--text-nav-primary); }
.ts-chat-md em { font-style: italic; }
.ts-chat-md del { text-decoration: line-through; opacity: 0.6; }

/* === Inline Code === */
.ts-chat-md code {
  font-family: "JetBrains Mono", "Cascadia Code", "Fira Code", monospace;
  font-size: 0.82em; background: rgba(255,255,255,0.06);
  padding: 1px 5px; border-radius: 4px; word-break: break-all;
}

/* === Code Blocks === */
.ts-chat-md pre {
  position: relative; max-width: 100%; overflow-x: auto;
  background: rgba(0,0,0,0.3); border: 1px solid var(--border-outline);
  border-radius: 10px; padding: 14px 16px; margin: 0.5em 0;
  font-size: 0.8rem; line-height: 1.55;
}
.ts-chat-md pre code {
  background: none; padding: 0; border-radius: 0;
  font-size: inherit; word-break: normal; overflow-wrap: normal;
  white-space: pre; display: block;
}
.ts-chat-md .code-block-wrapper { position: relative; }
.ts-chat-md .code-copy-btn {
  position: absolute; top: 8px; right: 8px;
  padding: 4px 10px; font-size: 11px; border-radius: 6px;
  background: rgba(255,255,255,0.08); color: var(--text-nav-tertiary);
  border: 1px solid var(--border-outline); cursor: pointer;
  opacity: 0; transition: opacity 0.15s;
}
.ts-chat-md .code-block-wrapper:hover .code-copy-btn { opacity: 1; }
.ts-chat-md .code-copy-btn:hover { background: rgba(255,255,255,0.14); color: var(--text-nav-primary); }
.ts-chat-md .code-copy-btn.copied { color: #22c55e; }

/* === Blockquotes === */
.ts-chat-md blockquote {
  margin: 0.4em 0; padding: 8px 14px;
  border-left: 3px solid #7c3aed;
  background: rgba(124,58,237,0.06); border-radius: 0 8px 8px 0;
  color: var(--text-nav-secondary);
}
.ts-chat-md blockquote p { margin: 0.2em 0; }

/* === Horizontal Rule === */
.ts-chat-md hr {
  border: none; border-top: 1px solid var(--border-outline);
  margin: 0.75em 0;
}

/* === Tables === */
.ts-chat-md table {
  max-width: 100%; border-collapse: collapse; margin: 0.5em 0;
  font-size: 0.85em; display: block; overflow-x: auto;
}
.ts-chat-md th, .ts-chat-md td {
  padding: 6px 12px; border: 1px solid var(--border-outline);
  text-align: left;
}
.ts-chat-md th {
  background: rgba(255,255,255,0.04); font-weight: 600;
  color: var(--text-nav-primary);
}
.ts-chat-md tr:nth-child(even) { background: rgba(255,255,255,0.02); }

/* === Task Lists === */
.ts-chat-md input[type="checkbox"] {
  margin-right: 6px; accent-color: #7c3aed;
}

/* === Images === */
.ts-chat-md img { max-width: 100%; height: auto; border-radius: 8px; margin: 0.4em 0; }

/* === Pygments Code Highlighting === */
.ts-chat-md .highlight { background: transparent; }
.ts-chat-md .highlight .hll { background-color: rgba(255,255,255,0.06); }
.ts-chat-md .highlight .c { color: #6b7280; font-style: italic; }  /* Comment */
.ts-chat-md .highlight .k { color: #c084fc; }  /* Keyword */
.ts-chat-md .highlight .s { color: #34d399; }  /* String */
.ts-chat-md .highlight .n { color: #e5e7eb; }  /* Name */
.ts-chat-md .highlight .o { color: #9ca3af; }  /* Operator */
.ts-chat-md .highlight .p { color: #9ca3af; }  /* Punctuation */
.ts-chat-md .highlight .nb { color: #60a5fa; }  /* Builtin */
.ts-chat-md .highlight .nc { color: #fbbf24; }  /* Class */
.ts-chat-md .highlight .nf { color: #60a5fa; }  /* Function */
.ts-chat-md .highlight .nd { color: #c084fc; }  /* Decorator */
.ts-chat-md .highlight .ni { color: #fbbf24; }  /* Entity */
.ts-chat-md .highlight .ne { color: #f87171; }  /* Exception */
.ts-chat-md .highlight .nn { color: #fbbf24; }  /* Namespace */
.ts-chat-md .highlight .nt { color: #c084fc; }  /* Tag */
.ts-chat-md .highlight .nv { color: #e5e7eb; }  /* Variable */
.ts-chat-md .highlight .vc { color: #e5e7eb; }  /* Class Variable */
.ts-chat-md .highlight .vg { color: #e5e7eb; }  /* Global Variable */
.ts-chat-md .highlight .vi { color: #e5e7eb; }  /* Instance Variable */
.ts-chat-md .highlight .m { color: #fb923c; }  /* Number */
.ts-chat-md .highlight .mi { color: #fb923c; }  /* Integer */
.ts-chat-md .highlight .mf { color: #fb923c; }  /* Float */
.ts-chat-md .highlight .bp { color: #60a5fa; }  /* Builtin Pseudo */
.ts-chat-md .highlight .kc { color: #c084fc; }  /* Keyword Constant */
.ts-chat-md .highlight .kd { color: #c084fc; }  /* Keyword Declaration */
.ts-chat-md .highlight .kn { color: #c084fc; }  /* Keyword Namespace */
.ts-chat-md .highlight .kp { color: #c084fc; }  /* Keyword Pseudo */
.ts-chat-md .highlight .kr { color: #c084fc; }  /* Keyword Reserved */
.ts-chat-md .highlight .kt { color: #c084fc; }  /* Keyword Type */
.ts-chat-md .highlight .ow { color: #c084fc; }  /* Operator Word */
.ts-chat-md .highlight .se { color: #34d399; }  /* String Escape */
.ts-chat-md .highlight .sh { color: #34d399; }  /* String Heredoc */
.ts-chat-md .highlight .si { color: #34d399; }  /* String Interpol */
.ts-chat-md .highlight .sx { color: #34d399; }  /* String Other */
.ts-chat-md .highlight .sr { color: #34d399; }  /* String Regex */
.ts-chat-md .highlight .s1 { color: #34d399; }  /* String Single */
.ts-chat-md .highlight .s2 { color: #34d399; }  /* String Double */
.ts-chat-md .highlight .sd { color: #6b7280; }  /* String Doc */
.ts-chat-md .highlight .err { color: #f87171; }  /* Error */
.ts-chat-md .highlight .gh { color: #e5e7eb; font-weight: bold; }  /* Heading */
.ts-chat-md .highlight .gu { color: #9ca3af; }  /* Subheading */
.ts-chat-md .highlight .ge { font-style: italic; }  /* Emphasized */
.ts-chat-md .highlight .gs { font-weight: bold; }  /* Strong */
</style>"""

_COPY_BUTTON_JS = r"""
(function() {
  var blocks = document.querySelectorAll('.ts-chat-md pre');
  blocks.forEach(function(pre) {
    if (pre.dataset.tsCopy) return;
    pre.dataset.tsCopy = '1';
    var wrapper = document.createElement('div');
    wrapper.className = 'code-block-wrapper';
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(pre);
    var btn = document.createElement('button');
    btn.className = 'code-copy-btn';
    btn.textContent = 'Copy';
    btn.onclick = function() {
      var code = pre.textContent || '';
      navigator.clipboard.writeText(code).then(function() {
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(function() { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
      });
    };
    wrapper.appendChild(btn);
  });
  if (blocks.length === 0) { setTimeout(arguments.callee, 100); }
})();
"""

_MD_CSS_INJECTED = False


def _ensure_md_css() -> None:
    global _MD_CSS_INJECTED
    if not _MD_CSS_INJECTED:
        ui.add_head_html(_MD_CSS)
        _MD_CSS_INJECTED = True


def _inject_copy_buttons() -> None:
    ui.run_javascript(_COPY_BUTTON_JS)


def _md_to_html(text: str) -> str:
    """Convert markdown to HTML with code highlighting."""
    try:
        import markdown2
        return markdown2.markdown(
            text,
            extras=[
                "fenced-code-blocks", "tables", "code-friendly",
                "cuddled-lists", "header-ids", "strike",
                "target-blank-links", "task_list", "highlightjs-lang",
                "footnotes", "spoiler",
            ],
        )
    except ImportError:
        pass
    try:
        import markdown
        return markdown.markdown(text, extensions=["fenced_code", "tables", "codehilite"])
    except ImportError:
        pass
    # Fallback: basic regex-based conversion
    return _basic_md_to_html(text)


def _basic_md_to_html(md: str) -> str:
    """Minimal markdown fallback."""
    result = []
    in_code = False
    for line in md.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
            tag = "<pre><code>" if in_code else "</code></pre>"
            result.append(tag)
            continue
        if in_code:
            result.append(line)
            continue
        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
        line = re.sub(r"\*(.+?)\*", r"<em>\1</em>", line)
        line = re.sub(r"`(.+?)`", r"<code>\1</code>", line)
        line = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', line)
        if line.startswith("### "):
            result.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            result.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            result.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("> "):
            result.append(f"<blockquote><p>{line[2:]}</p></blockquote>")
        elif line.strip():
            result.append(f"<p>{line}</p>")
        else:
            result.append("<br>")
    return "\n".join(result)


def render_message(msg: dict[str, str]) -> None:
    """Render a chat message bubble with enhanced markdown."""
    _ensure_md_css()
    role = msg["role"]
    agent = msg.get("agent", "")
    if role == "system":
        with ui.element("div").classes("flex justify-center my-2"):
            ui.label(msg["content"]).classes(
                "text-[11px] ts-text-tertiary italic px-3 py-1 rounded-full max-w-[90%] truncate"
            ).style("background:var(--bg-sidepanel)")
        return
    is_user = role == "user"
    with ui.element("div").classes("flex justify-start gap-2.5 items-start animate-fade-in"):
        if not is_user:
            _agent_avatar(agent)
        with ui.element("div").classes("max-w-[82%] overflow-hidden min-w-0"):
            if not is_user and agent:
                color = AGENT_COLORS.get(agent, "#999")
                label = AGENT_LABELS.get(agent, agent)
                ui.label(label).classes("text-[11px] font-medium mb-0.5").style(f"color:{color}")
            if is_user:
                _render_user_bubble(msg["content"])
            else:
                _render_agent_bubble(msg["content"])
        if is_user:
            _user_avatar()
    _inject_copy_buttons()


def _render_user_bubble(text: str) -> None:
    html = _render_mentions(text)
    with (
        ui.element("div")
        .classes("rounded-xl px-4 py-2.5 text-sm break-words ts-chat-md")
        .style(
            "background:var(--bg-sidepanel);color:var(--text-nav-primary);overflow-wrap:anywhere"
        )
    ):
        ui.html(html)


def _render_agent_bubble(text: str) -> None:
    html = _md_to_html(text)
    if "@" in text:
        html = _highlight_mentions_html(html)
    with ui.element("div").classes(
        "ts-bg-sidepanel rounded-xl px-4 py-2.5 text-sm ts-chat-md break-words"
    ):
        ui.html(html)


def _highlight_mentions_html(html: str) -> str:
    """Highlight @mentions in pre-rendered HTML."""
    def _replace(m: re.Match) -> str:
        name = m.group(1)
        color = AGENT_COLORS.get(name.lower(), "#f59e0b")
        return (
            f"<span style='color:{color};font-weight:600;"
            f"background:rgba(255,255,255,0.06);padding:0 4px;border-radius:4px'>"
            f"@{name}</span>"
        )
    return re.sub(r"@(\w+)", _replace, html)


def _render_mentions(text: str) -> str:
    def _replace(m: re.Match) -> str:
        name = m.group(1)
        color = AGENT_COLORS.get(name.lower(), "#f59e0b")
        return (
            f"<span style='color:{color};font-weight:600;"
            f"background:rgba(255,255,255,0.06);padding:0 4px;border-radius:4px'>"
            f"@{name}</span>"
        )
    return re.sub(r"@(\w+)", _replace, text)


def _agent_avatar(agent: str) -> None:
    color = AGENT_COLORS.get(agent, "#999")
    label = AGENT_LABELS.get(agent, agent)
    with (
        ui.element("div")
        .classes(
            "w-7 h-7 rounded-full flex items-center justify-center flex-none text-xs font-bold"
        )
        .style(f"background:{color};color:#fff")
    ):
        ui.label(label[:1])


def _user_avatar() -> None:
    with (
        ui.element("div")
        .classes(
            "w-7 h-7 rounded-full flex items-center justify-center flex-none text-xs font-bold"
        )
        .style("background:var(--fg-tertiary);color:var(--bg-app)")
    ):
        ui.label("U")
