#!/usr/bin/env python3
"""Export a Claude Code session (.jsonl) to a clean teaching transcript.

Two outputs from one parse:
  - Markdown (.md)   : plain-text record, renders on GitHub.
  - Chat HTML (.html): messaging-app look with right-aligned baby-blue user
                       bubbles and left-aligned pastel-green Claude bubbles.

Keeps: user prompts (verbatim), Claude's prose, skill invocations, Ask Q&A.
Collapses: tool actions into one-line "behind the scenes" summaries.
Drops: injected skill text, thinking, tool output, system/meta records.
"""
import json, os, sys, re, html
from datetime import datetime

# ----------------------------------------------------------------------------
# parsing
# ----------------------------------------------------------------------------
def basename(p):
    return os.path.basename(str(p).rstrip("/")) if p else ""

def first_line(s, n=100):
    s = " ".join(str(s).split())
    return (s[:n] + "…") if len(s) > n else s

def summarize_tool(name, inp):
    inp = inp or {}
    def g(k, d=""): return inp.get(k, d)
    if name == "Bash":
        desc = g("description"); cmd = first_line(g("command"), 90)
        return f"Ran command: `{cmd}`" + (f"  _( {desc} )_" if desc else "")
    if name == "Edit":         return f"Edited `{basename(g('file_path'))}`"
    if name == "Write":        return f"Wrote `{basename(g('file_path'))}`"
    if name == "Read":         return f"Read `{basename(g('file_path'))}`"
    if name == "NotebookEdit": return f"Edited notebook `{basename(g('notebook_path'))}`"
    if name in ("Task", "Agent"):
        return f"Dispatched a sub-agent: _{first_line(g('description') or g('prompt'), 80)}_"
    if name in ("TaskCreate", "TaskUpdate", "TaskList", "TaskGet"):
        return "__TASK__"
    if name == "ToolSearch":   return None
    if name == "Grep":         return f"Searched code for `{first_line(g('pattern'), 50)}`"
    if name == "Glob":         return f"Searched files matching `{g('pattern')}`"
    if name.startswith("mcp__Claude_Browser__"):
        return f"Browser preview: {name.split('__')[-1].replace('preview_', '')}"
    if name.startswith("mcp__"):
        return f"Used tool `{name.split('__')[-1]}`"
    return f"Used tool `{name}`"

SLASH_TAG = re.compile(r"^<([a-z0-9][a-z0-9-]*)-command>")
QA_PAIR   = re.compile(r'"([^"]+)"="([^"]+)"')

def clean_user_text(record, content):
    """Real user prompt text, a '__SLASH__/x' marker, or None if injected/meta."""
    if record.get("isMeta") or record.get("sourceToolUseID"):
        return None  # harness-injected skill text / auto-continue, never typed
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = [b.get("text", "") for b in content
                 if isinstance(b, dict) and b.get("type") == "text"]
        if not parts:
            return None
        text = "\n".join(parts)
    else:
        return None
    t = text.strip()
    if not t:
        return None
    m = SLASH_TAG.match(t)
    if m:
        return f"__SLASH__/{m.group(1)}"
    if t.startswith("<") or t.startswith("[Request interrupted"):
        return None
    if t.startswith("Caveat:") and "local commands" in t:
        return None
    return t

def parse_session(path, app_title, session_short):
    records = []
    for line in open(path, errors="replace"):
        try: records.append(json.loads(line))
        except: pass

    ask_ids, answers = set(), {}
    for r in records:
        m = r.get("message")
        if not isinstance(m, dict): continue
        c = m.get("content")
        if not isinstance(c, list): continue
        for b in c:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "AskUserQuestion":
                ask_ids.add(b.get("id"))
            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in ask_ids:
                tc = b.get("content")
                answers[b.get("tool_use_id")] = tc if isinstance(tc, str) else json.dumps(tc)

    ts = [r.get("timestamp") for r in records if r.get("timestamp")]
    def fmt(t):
        try: return datetime.fromisoformat(t.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except: return t or "?"
    date = fmt(ts[0]) if ts else "?"

    events, pending, nprompts = [], [], 0
    def flush():
        if pending:
            events.append(("tools", list(pending))); pending.clear()

    for r in records:
        rtype, m = r.get("type"), r.get("message")
        if rtype == "user" and isinstance(m, dict):
            txt = clean_user_text(r, m.get("content"))
            if txt:
                flush(); nprompts += 1
                if txt.startswith("__SLASH__"):
                    events.append(("slash", txt[len("__SLASH__"):]))
                else:
                    events.append(("user", txt))
        elif rtype == "assistant" and isinstance(m, dict):
            content = m.get("content")
            if not isinstance(content, list): continue
            texts = [b.get("text", "") for b in content
                     if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip()]
            if texts:
                flush(); events.append(("claude", "\n\n".join(texts).strip()))
            for b in content:
                if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                    continue
                nm = b.get("name")
                if nm == "Skill":
                    flush(); events.append(("skill", (b.get("input") or {}).get("skill", "?")))
                elif nm == "AskUserQuestion":
                    flush()
                    pairs = QA_PAIR.findall(answers.get(b.get("id"), ""))
                    if not pairs:
                        pairs = [(q.get("question", ""), "") for q in (b.get("input", {}).get("questions") or [])]
                    events.append(("ask", pairs))
                else:
                    s = summarize_tool(nm, b.get("input"))
                    if s is None: continue
                    if s == "__TASK__":
                        if not (pending and pending[-1] == "Updated the task checklist"):
                            pending.append("Updated the task checklist")
                    else:
                        pending.append(s)
    flush()
    meta = {"title": app_title, "short": session_short, "date": date, "nprompts": nprompts}
    return events, meta

# ----------------------------------------------------------------------------
# markdown renderer
# ----------------------------------------------------------------------------
def render_md(events, meta):
    out = [
        f"# {meta['title']} - how it was built",
        "",
        "> A clean transcript of the Claude Code conversation that built this app.",
        f"> Session `{meta['short']}` · {meta['date']} · {meta['nprompts']} prompts from Batu.",
        ">",
        "> Claude's tool actions (editing files, running commands, browsing the preview) are",
        "> collapsed into one-line summaries so the conversation reads as a narrative.",
        "",
    ]
    for kind, payload in events:
        if kind == "user":
            out += ["", "---", "", "### 🧔🏻‍♂️ Batu", "", payload, ""]
        elif kind == "slash":
            out += ["", "---", "", "### 🧔🏻‍♂️ Batu", "", f"Ran the `{payload}` slash command.", ""]
        elif kind == "claude":
            out += ["### 🤖 Claude", "", payload, ""]
        elif kind == "skill":
            out += [f"#### ⚡ Skill invoked: `{payload}`", "",
                    "<sub>*A short instruction expands into a full pre-built workflow that Claude now runs.*</sub>", ""]
        elif kind == "ask":
            out += ["#### 🤔 Claude checks in", ""]
            for q, a in payload:
                out.append(f"- **Q:** {q}")
                if a: out.append(f"  **Batu:** _{a}_")
            out.append("")
        elif kind == "tools":
            out += ["", "<sub>*Behind the scenes, Claude:*</sub>"]
            out += [f"> - {line}" for line in payload]
            out.append("")
    return "\n".join(out).rstrip() + "\n"

# ----------------------------------------------------------------------------
# tiny markdown -> html (inline code, bold, italics, fenced code, bullets)
# ----------------------------------------------------------------------------
def mini_md(text):
    text = text.replace("\r\n", "\n")
    blocks, i, n = [], 0, len(text)
    fence = re.split(r"(```.*?```)", text, flags=re.S)
    html_parts = []
    for seg in fence:
        if seg.startswith("```"):
            body = seg[3:-3]
            body = body.split("\n", 1)[1] if "\n" in body else body  # drop lang line
            html_parts.append("<pre><code>" + html.escape(body.strip("\n")) + "</code></pre>")
            continue
        # paragraph / list handling
        lines = seg.split("\n")
        buf, li = [], []
        def flush_p():
            if buf:
                html_parts.append("<p>" + "<br>".join(inline(x) for x in buf) + "</p>")
                buf.clear()
        def flush_li():
            if li:
                html_parts.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in li) + "</ul>")
                li.clear()
        for ln in lines:
            s = ln.rstrip()
            if re.match(r"^\s*[-*]\s+", s):
                flush_p(); li.append(re.sub(r"^\s*[-*]\s+", "", s))
            elif s.strip() == "":
                flush_p(); flush_li()
            else:
                flush_li(); buf.append(s)
        flush_p(); flush_li()
    return "".join(html_parts)

def inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"<em>\1</em>", s)
    return s

# ----------------------------------------------------------------------------
# chat html renderer
# ----------------------------------------------------------------------------
# Inline SVG avatars (no single emoji has beard + glasses). Batu: brown-haired
# bearded man with glasses on a blue field; Claude: friendly robot on green.
BATU_SVG = """<svg viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg">
<circle cx="22" cy="22" r="22" fill="#d7e6ff"/>
<circle cx="22" cy="21" r="12" fill="#6b4a2e"/>
<circle cx="22" cy="23" r="10" fill="#f0c69f"/>
<path d="M11 22 C11 12, 33 12, 33 22 C30.5 17.2, 13.5 17.2, 11 22 Z" fill="#6b4a2e"/>
<path d="M12.4 24.5 C13 33, 18 36, 22 36 C26 36, 31 33, 31.6 24.5 C29 29, 27 30.5, 22 30.5 C17 30.5, 15 29, 12.4 24.5 Z" fill="#6b4a2e"/>
<path d="M17.3 27.6 C19 29, 25 29, 26.7 27.6 C25 29.7, 19 29.7, 17.3 27.6 Z" fill="#5c3f27"/>
<g fill="#ffffff" fill-opacity="0.28" stroke="#2f2a26" stroke-width="1.1">
<rect x="13.2" y="20.2" width="7" height="5.4" rx="2.4"/>
<rect x="23.8" y="20.2" width="7" height="5.4" rx="2.4"/>
<path d="M20.2 22.4 C21 21.9, 23 21.9, 23.8 22.4" fill="none"/>
<path d="M13.2 22 L10.2 21.3" fill="none"/>
<path d="M30.8 22 L33.8 21.3" fill="none"/>
</g>
<circle cx="16.7" cy="23" r="1.05" fill="#3a2e26"/>
<circle cx="27.3" cy="23" r="1.05" fill="#3a2e26"/>
</svg>"""

CLAUDE_SVG = """<svg viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg">
<circle cx="22" cy="22" r="22" fill="#cdeeda"/>
<line x1="22" y1="10.5" x2="22" y2="14" stroke="#3f6b52" stroke-width="1.4"/>
<circle cx="22" cy="9.6" r="1.7" fill="#3f6b52"/>
<rect x="11.5" y="13.5" width="21" height="17.5" rx="6" fill="#f2fbf5" stroke="#3f6b52" stroke-width="1.4"/>
<rect x="9.2" y="19" width="2.6" height="6" rx="1.3" fill="#3f6b52"/>
<rect x="32.2" y="19" width="2.6" height="6" rx="1.3" fill="#3f6b52"/>
<circle cx="17.5" cy="21.5" r="2.5" fill="#3f6b52"/>
<circle cx="26.5" cy="21.5" r="2.5" fill="#3f6b52"/>
<circle cx="18.2" cy="20.8" r="0.8" fill="#fff"/>
<circle cx="27.2" cy="20.8" r="0.8" fill="#fff"/>
<path d="M17.5 26 C19.5 28.2, 24.5 28.2, 26.5 26" fill="none" stroke="#3f6b52" stroke-width="1.4" stroke-linecap="round"/>
</svg>"""

HTML_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - how it was built</title>
<style>
  :root {{
    --bg: #f5f7fb; --panel: #ffffff; --ink: #1c2430; --muted: #6b7683;
    --user-bg: rgba(96,165,250,.16); --user-br: rgba(96,165,250,.45);
    --ai-bg: rgba(74,201,155,.15);  --ai-br: rgba(74,201,155,.42);
    --skill-bg: rgba(245,181,74,.16); --skill-br: rgba(245,181,74,.5);
    --ask-bg: rgba(167,139,250,.13); --ask-br: rgba(167,139,250,.45);
    --bts-bg: rgba(120,132,148,.08); --bts-br: rgba(120,132,148,.22);
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#0e131a; --panel:#141b24; --ink:#e6ebf2; --muted:#93a0b0;
      --user-bg: rgba(96,165,250,.22); --ai-bg: rgba(74,201,155,.18);
      --bts-bg: rgba(150,165,185,.10); --bts-br: rgba(150,165,185,.20); }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
    font: 16px/1.55 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
  .wrap {{ max-width: 820px; margin: 0 auto; padding: 24px 18px 80px; }}
  header.top {{ text-align:center; padding: 18px 0 8px; }}
  header.top h1 {{ font-size: 1.5rem; margin: 0 0 6px; }}
  header.top .sub {{ color: var(--muted); font-size: .9rem; }}
  .row {{ display:flex; align-items:flex-end; gap:10px; margin: 14px 0; }}
  .row.user {{ flex-direction: row-reverse; }}
  .avatar {{ flex:0 0 auto; width:40px; height:40px; border-radius:50%; overflow:hidden;
    background:var(--panel); box-shadow: 0 1px 3px rgba(0,0,0,.12); }}
  .avatar svg, .avatar img {{ display:block; width:100%; height:100%; object-fit:cover; }}
  .avatar.batu, .avatar.bot {{ background-position:center; background-size:cover; background-repeat:no-repeat; }}
  .bubble {{ max-width: 76%; padding: 10px 14px; border-radius: 18px;
    border:1px solid transparent; word-wrap:break-word; }}
  .bubble p {{ margin: 0 0 .5em; }} .bubble p:last-child {{ margin-bottom:0; }}
  .bubble code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: .88em; background: rgba(130,140,160,.16); padding: .05em .35em; border-radius:6px; }}
  .bubble pre {{ background: rgba(130,140,160,.14); padding:10px 12px; border-radius:12px;
    overflow:auto; margin:.4em 0; }}
  .bubble pre code {{ background:none; padding:0; }}
  .user .bubble {{ background:var(--user-bg); border-color:var(--user-br); border-bottom-right-radius:6px; }}
  .ai   .bubble {{ background:var(--ai-bg); border-color:var(--ai-br); border-bottom-left-radius:6px; }}
  .name {{ font-size:.72rem; color:var(--muted); margin: 0 6px 3px; }}
  .col {{ display:flex; flex-direction:column; max-width:76%; }}
  .user .col {{ align-items:flex-end; }} .ai .col {{ align-items:flex-start; }}
  .col .bubble {{ max-width:100%; }}
  .skill, .ask {{ margin: 16px auto; max-width: 88%; }}
  .skill {{ text-align:center; }}
  .skill .pill {{ display:inline-block; background:var(--skill-bg); border:1px solid var(--skill-br);
    border-radius:999px; padding:7px 16px; font-weight:600; font-size:.92rem; }}
  .skill .note {{ color:var(--muted); font-size:.8rem; margin-top:5px; }}
  .ask {{ background:var(--ask-bg); border:1px solid var(--ask-br); border-radius:14px; padding:12px 16px; }}
  .ask h4 {{ margin:0 0 8px; font-size:.9rem; }}
  .ask .qa {{ margin:6px 0; }} .ask .q {{ font-weight:600; }}
  .ask .a {{ color:var(--muted); }} .ask .a b {{ color:var(--ink); font-style:italic; font-weight:600; }}
  .bts {{ margin: 8px 0 8px 50px; background:var(--bts-bg); border:1px solid var(--bts-br);
    border-radius:12px; padding:8px 12px; font-size:.82rem; color:var(--muted); }}
  .bts .hd {{ font-style:italic; margin-bottom:4px; }}
  .bts ul {{ margin:0; padding-left:18px; }} .bts li {{ margin:2px 0; }}
  .bts code {{ font-family: ui-monospace, Menlo, monospace; font-size:.92em;
    background:rgba(130,140,160,.16); padding:.02em .3em; border-radius:5px; }}
</style>
</head>
<body>
<div class="wrap">
<header class="top">
  <h1>{title}</h1>
  <div class="sub">How it was built &middot; session <code>{short}</code> &middot; {date} &middot; {nprompts} prompts from Batu</div>
</header>
"""

HTML_FOOT = "</div>\n</body>\n</html>\n"

def render_html(events, meta, batu_png_b64=None):
    import urllib.parse
    # Each avatar is defined ONCE as a CSS background so the image bytes appear a
    # single time per file instead of being repeated on every message.
    bot_uri = "data:image/svg+xml," + urllib.parse.quote(CLAUDE_SVG, safe="")
    css = [f'.avatar.bot{{background-image:url("{bot_uri}")}}']
    if batu_png_b64:
        css.append(f'.avatar.batu{{background-color:#fff;background-image:url("data:image/png;base64,{batu_png_b64}")}}')
        batu_avatar = '<div class="avatar batu"></div>'
    else:
        batu_avatar = f'<div class="avatar">{BATU_SVG}</div>'  # drawn-SVG fallback
    parts = [HTML_HEAD.format(**{k: html.escape(str(v)) for k, v in meta.items()}),
             "<style>" + "".join(css) + "</style>"]
    for kind, payload in events:
        if kind in ("user", "slash"):
            body = f"Ran the <code>{html.escape(payload)}</code> slash command." if kind == "slash" else mini_md(payload)
            parts.append(
                f'<div class="row user">{batu_avatar}'
                f'<div class="col"><div class="name">Batu</div><div class="bubble">{body}</div></div></div>')
        elif kind == "claude":
            parts.append(
                '<div class="row ai"><div class="avatar bot"></div>'
                f'<div class="col"><div class="name">Claude</div><div class="bubble">{mini_md(payload)}</div></div></div>')
        elif kind == "skill":
            parts.append(
                f'<div class="skill"><span class="pill">⚡ Skill invoked: <code>{html.escape(payload)}</code></span>'
                '<div class="note">A short instruction expands into a full pre-built workflow that Claude now runs.</div></div>')
        elif kind == "ask":
            qa = ['<div class="ask"><h4>🤔 Claude checks in</h4>']
            for q, a in payload:
                qa.append(f'<div class="qa"><div class="q">{inline(q)}</div>'
                          + (f'<div class="a">Batu: <b>{inline(a)}</b></div>' if a else "") + "</div>")
            qa.append("</div>")
            parts.append("".join(qa))
        elif kind == "tools":
            items = "".join(f"<li>{inline(x)}</li>" for x in payload)
            parts.append(f'<div class="bts"><div class="hd">Behind the scenes, Claude:</div><ul>{items}</ul></div>')
    parts.append(HTML_FOOT)
    return "\n".join(parts)

# ----------------------------------------------------------------------------
def load_avatar_b64(dst_md):
    """Base64 of <repo>/assets/avatar-batu.png, or None if absent."""
    import base64
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(dst_md))))
    p = os.path.join(repo, "assets", "avatar-batu.png")
    if not os.path.exists(p):
        return None
    return base64.b64encode(open(p, "rb").read()).decode()

if __name__ == "__main__":
    src, dst_md, title, short = sys.argv[1:5]
    events, meta = parse_session(src, title, short)
    with open(dst_md, "w") as f:
        f.write(render_md(events, meta))
    dst_html = os.path.splitext(dst_md)[0] + ".html"
    with open(dst_html, "w") as f:
        f.write(render_html(events, meta, batu_png_b64=load_avatar_b64(dst_md)))
    print(f"wrote {dst_md} and {dst_html}  ({meta['nprompts']} prompts)")
