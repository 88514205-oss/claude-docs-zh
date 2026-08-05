# -*- coding: utf-8 -*-
"""生成小说式文档阅读器页面（含关键词弹窗解释）+ 更新主页"""
import os, re, html as html_mod, datetime, json

base_dir = "/opt/AstrBot/data/workspaces/_-2_FriendMessage_88514205/claude_docs"
md_dir = os.path.join(base_dir, "md")
out_dir = os.path.join(base_dir, "doc")
os.makedirs(out_dir, exist_ok=True)

with open(os.path.join(base_dir, "_icons_cache.json")) as f:
    ICONS = json.load(f)
with open(os.path.join(base_dir, "_kw_data.json"), "r", encoding="utf-8") as f:
    KW_DATA = json.load(f)
try:
    with open(os.path.join(base_dir, "_kw_extra.json"), "r", encoding="utf-8") as f_extra:
        KW_EXTRA = json.load(f_extra)
except FileNotFoundError:
    KW_EXTRA = {}

ICON_DIR = "/opt/AstrBot/data/skills/tabler-icons-skill/icons/outline"
def _get_icon_svg(name):
    p = os.path.join(ICON_DIR, name + ".svg")
    if os.path.exists(p):
        with open(p) as fh:
            svg = fh.read()
        svg = re.sub(r'<!--.*?-->', '', svg, flags=re.S)
        svg = re.sub(r'\s+', ' ', svg).strip()
        svg = svg.replace('width="24" height="24"', 'width="1em" height="1em"')
        return svg
    return ""

EMOJI_SVG = {}
_emoji_map = {
    "📁": "folder", "🌿": "leaf", "⏱": "clock", "⏸": "player-pause", "⏵": "player-play",
    "✗": "x", "✓": "check", "✅": "check", "❌": "x",
    "💰": "coin", "🔗": "link", "👍": "thumb-up", "👎": "thumb-down",
    "🤖": "robot", "📊": "chart-bar", "✽": "star", "✻": "star", "✢": "star", "✱": "star",
}
for _e, _i in _emoji_map.items():
    _s = _get_icon_svg(_i)
    if _s:
        EMOJI_SVG[_e] = f'<span class="icon inline-emoji" aria-hidden="true">{_s}</span>'


def replace_kw_outside_tags(text):
    """关键词替换：跳过HTML标签内部，用占位符一次性替换避免嵌套"""
    kw_list = sorted(KW_DATA.keys(), key=lambda x: -len(x))
    parts = re.split(r'(<a [^>]*>.*?</a>|<code>.*?</code>)', text, flags=re.S)
    for i, part in enumerate(parts):
        if part.startswith("<a ") or part.startswith("<code>"):
            continue
        placeholders = {}
        for idx, kw in enumerate(kw_list):
            if kw in part:
                ph = f"\x00KW{idx}\x00"
                placeholders[ph] = kw
                part = part.replace(kw, ph)
        for ph, kw in placeholders.items():
            part = part.replace(ph, f'<a class="kw" onclick="showKw(\'{kw}\')" title="点击查看解释">{kw}</a>')
        parts[i] = part
    return "".join(parts)


def replace_emoji(text):
    """将正文中的emoji替换为SVG图标（保留内容箭头符号）"""
    for e, s in EMOJI_SVG.items():
        if e in text:
            text = text.replace(e, s)
    # 色块：红色/黄色/紫色语义色标
    text = text.replace("🔴", '<span class="dot dot-red"></span>')
    text = text.replace("🟡", '<span class="dot dot-yellow"></span>')
    text = text.replace("🟣", '<span class="dot dot-purple"></span>')
    text = text.replace("⛶", '<span class="icon" aria-hidden="true">{}</span>'.format(_get_icon_svg("maximize") or ""))
    text = text.replace("⤡", '<span class="icon" aria-hidden="true">{}</span>'.format(_get_icon_svg("arrow-autofit-width") or ""))
    return text



def icon(name, cls="icon"):
    svg = _get_icon_svg(name)
    if not svg and name in ICONS:
        svg = ICONS[name]
    return f'<span class="{cls}" aria-hidden="true">{svg}</span>'

files = sorted([f for f in os.listdir(md_dir) if f.endswith(".md") and f != "slash-commands.md"])
docs = []
for f in files:
    with open(os.path.join(md_dir, f), "r", encoding="utf-8") as fh:
        content = fh.read()
    title = ""
    m = re.search(r'^#\s+(.+)$', content, re.M)
    if m:
        title = m.group(1).strip()
    else:
        m = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.S)
        if m:
            title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    if not title:
        title = f.replace(".md", "").replace("_", " ")
    size_kb = len(content.encode('utf-8')) / 1024
    docs.append({"name": f.replace(".md",""), "title": title, "content": content, "size_kb": size_kb})


def clean_mdx(text):
    """移除export const代码块"""
    lines = text.split("\n")
    out = []
    in_export = False
    for line in lines:
        if line.startswith("export const"):
            in_export = True
            continue
        if in_export:
            if line.startswith("#"):
                in_export = False
                out.append(line)
            continue
        out.append(line)
    return "\n".join(out)

def convert_mdx_blocks(text):
    """多行MDX组件转HTML"""
    def cardgroup_repl(m):
        inner = m.group(1)
        cards = re.findall(r'<Card\s+title="([^"]*)"(?:\s+icon="([^"]*)")?(?:\s+href="([^"]*)")?[^>]*>(.*?)</Card>', inner, re.S)
        if not cards:
            return ""
        html = ['<div class="card-group">']
        for title, icon, href, desc in cards:
            desc = desc.strip().replace("\n", " ")
            link_open = f'<a class="mg-card" href="{href}" target="_blank" rel="noopener">' if href else '<div class="mg-card">'
            link_close = "</a>" if href else "</div>"
            icon_html = f'<span class="mg-icon">{icon}</span>' if icon else ""
            html.append(f'{link_open}{icon_html}<div class="mg-card-body"><div class="mg-card-title">{title}</div><div class="mg-card-desc">{desc}</div></div>{link_close}')
        html.append("</div>")
        return "\n".join(html)
    text = re.sub(r'<CardGroup[^>]*>(.*?)</CardGroup>', cardgroup_repl, text, flags=re.S)
    callout_map = {"Tip": "tip", "Note": "note", "Warning": "warning", "Info": "info"}
    for tag, ctype in callout_map.items():
        text = re.sub(rf'<{tag}[^>]*>(.*?)</{tag}>', lambda m, ct=ctype: f'<div class="callout callout-{ct}">{m.group(1)}</div>', text, flags=re.S)
    text = re.sub(r'<Callout\s+type="([^"]*)"[^>]*>(.*?)</Callout>', lambda m: f'<div class="callout callout-{m.group(1)}">{m.group(2)}</div>', text, flags=re.S)
    text = re.sub(r'<Callout[^>]*>(.*?)</Callout>', lambda m: f'<div class="callout">{m.group(1)}</div>', text, flags=re.S)
    def steps_repl(m):
        inner = m.group(1)
        steps = re.findall(r'<Step\s+title="([^"]*)"[^>]*>(.*?)</Step>', inner, re.S)
        html = ['<ol class="steps">']
        for title, body in steps:
            html.append(f'<li><div class="step-title">{title}</div>{body}</li>')
        html.append("</ol>")
        return "\n".join(html)
    text = re.sub(r'<Steps[^>]*>(.*?)</Steps>', steps_repl, text, flags=re.S)
    text = re.sub(r'<Steps[^>]*>\s*', '<ol class="steps">', text)
    text = re.sub(r'</Steps>', '</ol>', text)
    text = re.sub(r'<Step\s+title="([^"]*)"[^>]*>', lambda m: f'<li><div class="step-title">{m.group(1)}</div>', text)
    text = re.sub(r'<Step[^>]*>', '<li>', text)
    text = re.sub(r'</Step>', '</li>', text)
    def tabs_repl(m):
        inner = m.group(1)
        tabs = re.findall(r'<Tab\s+(?:label|title)="([^"]*)"[^>]*>(.*?)</Tab>', inner, re.S)
        html = ['<div class="tabs">']
        for label, body in tabs:
            html.append(f'<div class="tab-item"><div class="tab-label">{label}</div><div class="tab-body">{body}</div></div>')
        html.append("</div>")
        return "\n".join(html)
    text = re.sub(r'<Tabs[^>]*>(.*?)</Tabs>', tabs_repl, text, flags=re.S)
    def acc_repl(m):
        inner = m.group(1)
        items = re.findall(r'<Accordion\s+title="([^"]*)"[^>]*>(.*?)</Accordion>', inner, re.S)
        html = ['<div class="acc-group">']
        for title, body in items:
            html.append(f'<details class="acc"><summary>{title}</summary>{body}</details>')
        html.append("</div>")
        return "\n".join(html)
    text = re.sub(r'<AccordionGroup[^>]*>(.*?)</AccordionGroup>', acc_repl, text, flags=re.S)
    text = re.sub(r'</?CodeGroup[^>]*>', '', text)
    text = re.sub(r'</?Frame[^>]*>', '', text)
    text = re.sub(r'<Esc\s*/>', '<kbd>Esc</kbd>', text)
    text = re.sub(r'</?Esc>', '<kbd>Esc</kbd>', text)
    text = re.sub(r'<KEY\s+name="([^"]*)"\s*/>', lambda m: f'<kbd>{m.group(1)}</kbd>', text)
    text = re.sub(r'<KEY\s+name="([^"]*)"[^>]*>', lambda m: f'<kbd>{m.group(1)}</kbd>', text)
    text = re.sub(r'</?KEY>', '', text)
    text = re.sub(r'<A\s+href="([^"]*)"[^>]*>(.*?)</A>', lambda m: f'<a href="{m.group(1)}">{m.group(2)}</a>', text, flags=re.S)
    text = re.sub(r'<C[^>]*>(.*?)</C>', lambda m: f'<code>{m.group(1)}</code>', text, flags=re.S)
    text = re.sub(r'</?(?:Tabs|Tab)[^>]*>', '\n', text)
    return text



def convert_inline_links(text, doc_name):
    """将 [text](url) 改写为关键词模版样式（紫色虚线+弹抽屉），不保留跳转"""
    def repl(m):
        txt = re.sub(r'[*`]', '', m.group(1)).strip()
        if not txt:
            return ""
        return f'<a class="kw" onclick="showKw(\'{txt}\')" title="点击查看解释">{txt}</a>'
    text = re.sub(r'\[([^\[\]]+)\]\(([^()]+)\)', repl, text)
    return text


def clean_basic_html(text):
    """清理官方文档残留的基础HTML标签（h2/h3/div/span/p等），保护代码块内容"""
    # 1. 保护代码块
    code_blocks = []
    def save_code(m):
        code_blocks.append(m.group(0))
        return f"\x00CODE{len(code_blocks)-1}\x00"
    text = re.sub(r'```.*?```', save_code, text, flags=re.S)

    # 2. 成对标题标签 -> markdown标题（保留TOC）
    for tag, md in [("h2", "##"), ("h3", "###"), ("h4", "####")]:
        text = re.sub(
            rf'<{tag}[^>]*>\s*(.*?)\s*</{tag}>',
            lambda m, md=md: f'\n{md} {re.sub(r"<[^>]+>", "", m.group(1)).strip()}\n',
            text, flags=re.S
        )

    # 3. 删除容器/行内标签（保留内容）
    text = re.sub(r'</?(?:div|span|p|br|hr|section|article|header|footer|main|aside|nav|figure|figcaption|table|thead|tbody|tr|td|th|ul|ol|li|blockquote|pre)[^>]*>', '\n', text)

    # 4. 删除孤立标题标签残留
    text = re.sub(r'</?h[1-6][^>]*>', '\n', text)

    # 5. 清理多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 6. 恢复代码块
    def restore_code(m):
        idx = int(m.group(1))
        return code_blocks[idx]
    text = re.sub(r'\x00CODE(\d+)\x00', restore_code, text)
    return text


def md_to_reader_html(md_text, doc_name):
    md_text = convert_mdx_blocks(clean_basic_html(clean_mdx(md_text)))
    lines = md_text.split("\n")
    out = []
    toc = []
    in_code = False
    in_table = False
    table_html = []
    counters = {}
    for line in lines:
        if line.startswith("```"):
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                out.append("<pre><code>")
                in_code = True
            continue
        if in_code:
            out.append(html_mod.escape(line))
            continue
        hm = re.match(r'^(#{1,4})\s+(.+)$', line)
        if hm:
            level = len(hm.group(1))
            text = hm.group(2).strip()
            tag = f"h{min(level+1,5)}"
            counters["_g"] = counters.get("_g", 0) + 1
            anchor = f"sec-{doc_name}-{counters['_g']}"
            toc.append((level, text, anchor))
            out.append(f'<{tag} id="{anchor}">{html_mod.escape(text)}</{tag}>')
            continue
        if line.startswith("> "):
            out.append(f"<blockquote>{html_mod.escape(line[2:])}</blockquote>")
        elif line.startswith("- "):
            li_text = html_mod.escape(line[2:])
            li_text = convert_inline_links(li_text, doc_name)
            li_text = replace_kw_outside_tags(li_text)
            li_text = replace_emoji(li_text)
            out.append(f"<li>{li_text}</li>")
        elif line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            is_sep = all(re.match(r'^:?-{2,}:?$', c) for c in cells)
            if not is_sep:
                def process_cell(cell):
                    cell = html_mod.escape(cell)
                    cell = convert_inline_links(cell, doc_name)
                    cell = replace_kw_outside_tags(cell)
                    cell = replace_emoji(cell)
                    return cell
                if not in_table:
                    in_table = True
                    out.append("<div class='table-wrap'><table>")
                if table_html == []:
                    out.append("<tr>" + "".join(f"<th>{process_cell(c)}</th>" for c in cells) + "</tr>")
                else:
                    out.append("<tr>" + "".join(f"<td>{process_cell(c)}</td>" for c in cells) + "</tr>")
                table_html.append(line)
            continue
        elif line == "":
            if in_table:
                out.append("</table></div>")
                in_table = False
                table_html = []
            out.append("")
        else:
            stripped = line.strip()
            # convert_mdx_blocks生成的组件HTML直接输出（不转义）
            if stripped.startswith("<div") or stripped.startswith("</div>") or stripped.startswith("<ol class"):
                out.append(line)
                continue
            escaped = html_mod.escape(line)
            escaped = convert_inline_links(escaped, doc_name)
            escaped = replace_kw_outside_tags(escaped)
            escaped = replace_emoji(escaped)
            out.append(f"<p>{escaped}</p>")
    if in_table:
        out.append("</table></div>")
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out), toc

def toc_html(toc):
    if not toc:
        return "<p style='color:var(--muted);font-size:13px;padding:8px;'>本文档无子章节</p>"
    items = []
    for level, text, anchor in toc:
        pad = (level - 1) * 14
        fs = 13.5 if level == 2 else 13
        items.append(f'<a href="#{anchor}" style="padding-left:{pad}px;font-size:{fs}px;">{html_mod.escape(text)}</a>')
    return "\n".join(items)

KW_JS_DATA = json.dumps(KW_DATA, ensure_ascii=False)
KW_JS_EXTRA = json.dumps(KW_EXTRA, ensure_ascii=False)

KW_CSS = """
/* ===== 关键词弹窗 ===== */
.kw-panel { position:fixed; left:0; top:50%; transform:translate(-110%,-50%); z-index:400; background:var(--card); border:1px solid var(--accent); border-left:none; border-radius:0 16px 16px 0; box-shadow:0 8px 40px rgba(0,0,0,0.6); transition:transform 0.35s cubic-bezier(0.22,1,0.36,1); max-height:70vh; display:flex; flex-direction:column; }
.kw-panel.open { transform:translate(0,-50%); }
.kw-panel .kwp-head { display:flex; align-items:center; gap:8px; padding:14px 18px 10px; border-bottom:1px solid var(--border); }
.kw-panel .kwp-badge { background:var(--kw-bg); color:var(--accent2); font-size:12px; font-weight:700; padding:3px 10px; border-radius:10px; flex-shrink:0; }
.kw-panel .kwp-title { font-size:15px; font-weight:600; color:var(--text); flex:1; line-height:1.4; }
.kw-panel .kwp-close { background:none; border:none; color:var(--muted); font-size:20px; cursor:pointer; padding:0 4px; line-height:1; flex-shrink:0; }
.kw-panel .kwp-close:hover { color:var(--text); }
.kw-panel .kwp-body { padding:14px 18px; overflow-y:auto; flex:1; }
.kw-panel .kwp-desc { font-size:14px; line-height:1.8; color:var(--text2); }
.kw-panel .kwp-link { display:inline-flex; align-items:center; margin-top:12px; color:var(--accent2); text-decoration:none; font-size:13px; font-weight:600; }
.kw-panel .kwp-link:hover { color:var(--accent); }
.kw-panel .kwp-bar-wrap { height:4px; background:var(--card2); border-radius:0 0 16px 0; overflow:hidden; flex-shrink:0; }
.kw-panel .kwp-bar { height:100%; width:100%; background:linear-gradient(90deg,var(--accent),var(--accent2)); border-radius:0 0 16px 0; }
"""

READER_CSS = """
:root {
  --bg: #0f1117; --bg2: #16181f; --card: #1b1e26; --card2: #20242e;
  --border: #2a2e3a; --text: #e2e4ea; --text2: #9aa0ad; --muted: #6b7280;
  --accent: #8b7cff; --accent2: #a99dff; --code-bg: #0c0e13;
  --kw-bg: rgba(139,124,255,0.15); --kw-hover: rgba(139,124,255,0.28);
}
* { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
html { scroll-behavior:smooth; }
body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; background:var(--bg); color:var(--text); }
.icon { display:inline-flex; vertical-align:-0.2em; width:1.1em; height:1.1em; margin-right:6px; }
.icon svg { width:100%; height:100%; }
.progress-bar { position:fixed; top:0; left:0; height:3px; background:var(--accent); width:0%; z-index:300; transition:width 0.1s linear; }
.topbar { position:fixed; top:0; left:0; right:0; z-index:200; background:rgba(22,24,31,0.92); backdrop-filter:blur(8px); border-bottom:1px solid var(--border); display:flex; align-items:center; padding:0 12px; height:52px; }
.topbar .tb-home { display:flex; align-items:center; color:var(--text2); text-decoration:none; font-size:14px; padding:6px 10px; border-radius:8px; }
.topbar .tb-home:hover { color:var(--text); background:var(--card2); }
.topbar .tb-title { flex:1; text-align:center; font-size:15px; font-weight:600; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; padding:0 10px; }
.topbar .tb-toc { background:none; border:1px solid var(--border); color:var(--text2); border-radius:8px; padding:6px 10px; cursor:pointer; font-size:13px; display:flex; align-items:center; }
.topbar .tb-toc:hover { color:var(--text); border-color:var(--accent); }
.reader { display:flex; padding-top:52px; min-height:100vh; }
.toc-side { width:240px; flex-shrink:0; position:sticky; top:52px; height:calc(100vh - 52px); overflow-y:auto; padding:20px 12px; border-right:1px solid var(--border); background:var(--bg); display:none; }
.toc-side h3 { font-size:13px; color:var(--muted); margin-bottom:10px; padding-left:8px; letter-spacing:1px; }
.toc-side a { display:block; color:var(--text2); text-decoration:none; padding:6px 8px; border-radius:6px; font-size:13px; line-height:1.5; border-left:2px solid transparent; }
.toc-side a:hover { color:var(--text); background:var(--card2); border-left-color:var(--accent); }
.toc-drawer { position:fixed; top:0; right:-300px; width:280px; max-width:85vw; height:100vh; background:var(--bg2); z-index:250; transition:right 0.25s ease; overflow-y:auto; padding:70px 16px 30px; border-left:1px solid var(--border); }
.toc-drawer.open { right:0; }
.toc-drawer h3 { font-size:14px; color:var(--muted); margin-bottom:12px; }
.toc-drawer a { display:block; color:var(--text2); text-decoration:none; padding:8px 6px; border-radius:6px; font-size:14px; line-height:1.5; }
.toc-drawer a:hover { color:var(--text); background:var(--card2); }
.overlay { position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:240; display:none; }
.overlay.show { display:block; }
.article { flex:1; max-width:760px; margin:0 auto; padding:40px 24px 80px; min-width:0; }
.article h1 { font-size:26px; margin-bottom:6px; line-height:1.4; }
.article .doc-meta { color:var(--muted); font-size:13px; margin-bottom:28px; padding-bottom:20px; border-bottom:1px solid var(--border); }
.article h2 { font-size:21px; margin:36px 0 14px; color:var(--text); line-height:1.4; }
.article h3 { font-size:18px; margin:28px 0 12px; color:var(--text); }
.article h4 { font-size:16px; margin:22px 0 10px; color:var(--accent2); }
.article p { font-size:16.5px; line-height:1.95; margin:14px 0; color:var(--text); }
.article li { margin-left:24px; line-height:1.9; font-size:16px; color:var(--text); }
.article a { color:#a78bfa; text-decoration:underline; text-underline-offset:3px; transition:color 0.15s; }
.article a:hover { color:#c4b5fd; }
.article a:visited { color:#a78bfa; }
.article a.kw { color:#c4b5fd; text-decoration:none; }
.article blockquote { border-left:4px solid var(--accent); padding:10px 16px; background:rgba(139,124,255,0.08); margin:16px 0; color:var(--text2); font-size:15px; border-radius:0 8px 8px 0; }
.article pre { background:var(--code-bg); color:#d5d8e0; padding:16px 18px; border-radius:10px; overflow-x:auto; -webkit-overflow-scrolling:touch; font-size:13.5px; line-height:1.7; margin:16px 0; white-space:pre; border:1px solid var(--border); }
.article code { font-family:"JetBrains Mono",Consolas,monospace; }
.article .table-wrap { overflow-x:auto; -webkit-overflow-scrolling:touch; margin:16px 0; border-radius:8px; border:1px solid var(--border); }
.article table { width:100%; border-collapse:collapse; font-size:14px; min-width:420px; }
.article th, .article td { border-bottom:1px solid var(--border); padding:9px 12px; text-align:left; color:var(--text); line-height:1.7; }
.article th { background:var(--card2); color:var(--accent2); }
.kw { color:#c4b5fd; background:var(--kw-bg); border-bottom:1px dashed var(--accent); padding:1px 4px; border-radius:4px; text-decoration:none; cursor:pointer; font-weight:500; transition:all 0.15s; }
.kw:hover { background:var(--kw-hover); color:#fff; }
.pager { max-width:760px; margin:0 auto; padding:0 24px 60px; display:flex; gap:12px; }
.pager a { flex:1; display:block; background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px 18px; text-decoration:none; transition:0.2s; }
.pager a:hover { border-color:var(--accent); transform:translateY(-2px); }
.pager .dir { font-size:12px; color:var(--muted); display:block; margin-bottom:6px; }
.pager .ptitle { font-size:15px; color:var(--text); font-weight:600; display:block; }
.pager a.next { text-align:right; }
.pager a:empty { display:none; }
.scroll-top { position:fixed; right:16px; bottom:20px; width:44px; height:44px; border-radius:50%; background:var(--card2); color:var(--text); border:1px solid var(--border); box-shadow:0 3px 12px rgba(0,0,0,0.4); display:none; z-index:90; align-items:center; justify-content:center; cursor:pointer; }
.scroll-top.show { display:flex; }
.scroll-top .icon { margin:0; width:1.4em; height:1.4em; }

.hamburger { background:none; border:none; color:var(--text); cursor:pointer; padding:8px; line-height:1; display:inline-flex; align-items:center; }
.topbar .logo { display:flex; align-items:center; font-weight:700; font-size:15px; color:var(--text); flex-shrink:0; }
.topbar .logo .icon { color:var(--accent); }
.drawer { position:fixed; top:0; left:0; bottom:0; width:250px; background:var(--bg2); color:var(--text); z-index:250; transform:translateX(-100%); transition:transform 0.25s ease; overflow-y:auto; padding-top:60px; border-right:1px solid var(--border); }
.drawer.open { transform:translateX(0); }
.drawer nav a { display:flex; align-items:center; padding:12px 20px; color:var(--text2); text-decoration:none; font-size:15px; }
.drawer nav a:hover, .drawer nav a:active { color:var(--text); background:var(--card2); }
.drawer a { display:block; color:var(--text2); text-decoration:none; padding:7px 20px; font-size:13.5px; line-height:1.5; }
.drawer a:hover { color:var(--text); background:var(--card2); }
.overlay { position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:240; display:none; }
.overlay.show { display:block; }


/* ===== MDX组件样式 ===== */
.card-group { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin:16px 0; }
.mg-card { display:flex; align-items:flex-start; gap:10px; background:var(--card); border:1px solid var(--border); border-radius:10px; padding:14px; text-decoration:none; transition:0.2s; }
.mg-card:hover { border-color:var(--accent); transform:translateY(-2px); }
.mg-icon { font-size:20px; flex-shrink:0; color:var(--accent); }
.mg-card-title { font-size:14px; font-weight:600; color:var(--text); margin-bottom:4px; }
.mg-card-desc { font-size:12.5px; color:var(--text2); line-height:1.5; }
.callout { border-left:4px solid var(--accent); padding:10px 16px; margin:14px 0; border-radius:0 8px 8px 0; font-size:14.5px; line-height:1.7; color:var(--text2); }
.callout-tip { border-left-color:#4caf50; background:rgba(76,175,80,0.08); }
.callout-note { border-left-color:#42a5f5; background:rgba(66,165,245,0.08); }
.callout-warning { border-left-color:#ff9800; background:rgba(255,152,0,0.08); }
.callout-info { border-left-color:#8b7cff; background:rgba(139,124,255,0.08); }
.steps { list-style:none; counter-reset:step; margin:16px 0; padding:0; }
.steps > li { position:relative; padding:0 0 16px 44px; margin:0; }
.steps > li::before { counter-increment:step; content:counter(step); position:absolute; left:0; top:2px; width:28px; height:28px; border-radius:50%; background:var(--accent); color:#fff; font-size:13px; font-weight:700; display:flex; align-items:center; justify-content:center; }
.step-title { font-weight:600; color:var(--text); margin-bottom:6px; font-size:15px; }
.tabs { margin:16px 0; }
.tab-item { background:var(--card); border:1px solid var(--border); border-radius:10px; margin-bottom:10px; overflow:hidden; }
.tab-label { padding:9px 14px; font-size:13px; font-weight:600; color:var(--accent2); background:var(--card2); border-bottom:1px solid var(--border); }
.tab-body { padding:12px 14px; }
.acc-group { margin:16px 0; }
.acc { background:var(--card); border:1px solid var(--border); border-radius:10px; margin-bottom:8px; overflow:hidden; }
.acc summary { padding:12px 16px; cursor:pointer; font-size:14px; font-weight:600; color:var(--text); }
.acc summary:hover { background:var(--card2); }
.acc[open] summary { border-bottom:1px solid var(--border); }
.article kbd { background:var(--card2); border:1px solid var(--border); border-bottom-width:2px; border-radius:5px; padding:1px 7px; font-size:12px; font-family:inherit; color:var(--text); }


.dot { display:inline-block; width:0.85em; height:0.85em; border-radius:50%; vertical-align:-0.1em; margin:0 2px; }
.dot-red { background:#f03e3e; }
.dot-yellow { background:#f59f00; }
.dot-purple { background:#9c36b5; }

@media (min-width: 1024px) { .toc-side { display:block; } .tb-toc { display:none; } }
@media (max-width: 1023px) { .article { padding:32px 18px 60px; } .article p { font-size:16px; } }
"""

KW_JS = """
// ===== 关键词弹窗逻辑 =====
const KW_DATA = __KW_DATA__;
  const KW_EXTRA = __KW_EXTRA__;
let kwTimer = null;
function showKw(kw) {
  const d = KW_DATA[kw] || KW_EXTRA[kw];
  if (!d) {
    document.getElementById('kwpBadge').textContent = kw;
    document.getElementById('kwpTitle').textContent = kw;
    document.getElementById('kwpDesc').textContent = '暂无该词条详细解释，可前往官方文档查阅。';
    document.getElementById('kwpLink').style.display = 'none';
    const panel = document.getElementById('kwPanel');
    panel.style.width = '320px';
    panel.classList.add('open');
    const bar = document.getElementById('kwBar');
    bar.style.transition = 'none';
    bar.style.width = '100%';
    void bar.offsetWidth;
    bar.style.transition = 'width 4s linear';
    bar.style.width = '0%';
    clearTimeout(kwTimer);
    kwTimer = setTimeout(hideKw, 4000);
    return;
  }
  document.getElementById('kwpBadge').textContent = kw;
  document.getElementById('kwpTitle').textContent = d.title;
  document.getElementById('kwpDesc').textContent = d.desc;
  var _kwpPfx = location.pathname.indexOf('/doc/') !== -1 || location.pathname.endsWith('/doc/') ? '' : 'doc/';
  document.getElementById('kwpLink').style.display = '';
  document.getElementById('kwpLink').href = _kwpPfx + d.doc + '.html';
  // 弹窗宽度随内容自适应（280-480px）
  const panel = document.getElementById('kwPanel');
  const estW = Math.min(480, Math.max(300, 280 + d.desc.length * 0.5));
  panel.style.width = estW + 'px';
  // 进度条时长按文本长度：每55字1秒，限4-14秒
  const dur = Math.min(14, Math.max(4, Math.round(d.desc.length / 55)));
  panel.classList.add('open');
  // 重置进度条动画
  const bar = document.getElementById('kwBar');
  bar.style.transition = 'none';
  bar.style.width = '100%';
  void bar.offsetWidth;
  bar.style.transition = 'width ' + dur + 's linear';
  bar.style.width = '0%';
  clearTimeout(kwTimer);
  kwTimer = setTimeout(hideKw, dur * 1000);
}
function hideKw() {
  document.getElementById('kwPanel').classList.remove('open');
  clearTimeout(kwTimer);
}
"""

total = len(docs)
for i, d in enumerate(docs):
    body_html, toc = md_to_reader_html(d["content"], d["name"])
    prev_doc = docs[i-1] if i > 0 else None
    next_doc = docs[i+1] if i < total-1 else None
    prev_html = f'<a href="{prev_doc["name"]}.html"><span class="dir">← 上一篇</span><span class="ptitle">{html_mod.escape(prev_doc["title"])}</span></a>' if prev_doc else '<a></a>'
    next_html = f'<a class="next" href="{next_doc["name"]}.html"><span class="dir">下一篇 →</span><span class="ptitle">{html_mod.escape(next_doc["title"])}</span></a>' if next_doc else '<a></a>'
    toc_side = toc_html(toc)
    toc_drawer = toc_html(toc)
    kw_js_filled = KW_JS.replace("__KW_DATA__", KW_JS_DATA).replace("__KW_EXTRA__", KW_JS_EXTRA)

    page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#0f1117">
<title>{html_mod.escape(d["title"])} - Claude Code 知识库</title>
<style>{READER_CSS}
{KW_CSS}</style>
</head>
<body>
<div class="progress-bar" id="progressBar"></div>
<header class="topbar">
  <span class="logo">{icon('book')}Claude Code 知识库</span>
  <div class="tb-title">{html_mod.escape(d["title"])}</div>
  <button class="hamburger" onclick="toggleDrawer()" aria-label="菜单">{icon('menu-2')}</button>
</header>
<aside class="drawer" id="drawer">
  <nav>
    <a href="../index.html" onclick="closeDrawer()">{icon('home')}返回首页</a>
    <a href="../index.html#index" onclick="closeDrawer()">{icon('file-text')}文档索引</a>
    <a href="../index.html#manual" onclick="closeDrawer()">{icon('book-2')}入门手册</a>
    <a href="../index.html#docs" onclick="closeDrawer()">{icon('file-text')}全部文档</a>
    <a href="#" onclick="closeDrawer();openRpt()">{icon('bug')}文档有误？汇报</a>
  </nav>
  <div style="margin:14px 20px 6px;font-size:12px;color:var(--muted);letter-spacing:1px;">本文目录</div>
  {toc_side}
</aside>
<div class="overlay" id="overlay" onclick="closeDrawer()"></div>

<div class="reader">
  <aside class="toc-side">
    <h3>本文目录</h3>
    {toc_side}
  </aside>

  <main class="article">
    {body_html}
  </main>
</div>

<nav class="pager">
  {prev_html}
  {next_html}
</nav>

<button class="scroll-top" id="scrollTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" aria-label="返回顶部">{icon('arrow_up')}</button>

<!-- 关键词解释弹窗 -->
<div class="kw-panel" id="kwPanel">
  <div class="kwp-head">
    <span class="kwp-badge" id="kwpBadge"></span>
    <span class="kwp-title" id="kwpTitle"></span>
    <button class="kwp-close" onclick="hideKw()">×</button>
  </div>
  <div class="kwp-body">
    <div class="kwp-desc" id="kwpDesc"></div>
    <a class="kwp-link" id="kwpLink" target="_blank">阅读完整文档{icon('arrow-right')}</a>
  </div>
  <div class="kwp-bar-wrap"><div class="kwp-bar" id="kwBar"></div></div>
</div>

<script>
function toggleDrawer() {{
  document.getElementById('drawer').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('show');
}}
function closeDrawer() {{
  document.getElementById('drawer').classList.remove('open');
  document.getElementById('overlay').classList.remove('show');
}}
window.addEventListener('scroll', function() {{
  var st = document.getElementById('scrollTop');
  st.classList.toggle('show', window.scrollY > 400);
  var h = document.documentElement.scrollHeight - window.innerHeight;
  var pct = h > 0 ? (window.scrollY / h * 100) : 0;
  document.getElementById('progressBar').style.width = pct + '%';
}});
{kw_js_filled}
</script>
</body>
</html>'''
    with open(os.path.join(out_dir, d["name"] + ".html"), "w", encoding="utf-8") as f:
        f.write(page)

print(f"✅ 生成完成：{total} 个阅读器页面（含关键词弹窗）")
for d in docs[:3]:
    p = os.path.join(out_dir, d["name"] + ".html")
    print(f"  {d['name']}.html ({os.path.getsize(p)/1024:.1f}KB)")
