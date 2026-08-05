# -*- coding: utf-8 -*-
"""重新生成主页（含全部64文档+链接转换+emoji+汇报+更新日志+雨云）"""
import os, re, html as html_mod, datetime, json

base_dir = "/opt/AstrBot/data/workspaces/_-2_FriendMessage_88514205/claude_docs"
index_path = os.path.join(base_dir, "index.html")
md_dir = os.path.join(base_dir, "md")
icons_base = "/opt/AstrBot/data/skills/tabler-icons-skill/icons/outline"

def get_svg(name):
    p = os.path.join(icons_base, name + ".svg")
    if os.path.exists(p):
        with open(p) as fh:
            svg = fh.read()
        svg = re.sub(r'<!--.*?-->', '', svg, flags=re.S)
        svg = re.sub(r'\s+', ' ', svg).strip()
        svg = svg.replace('width="24" height="24"', 'width="1em" height="1em"')
        return svg
    return ""

def icon(name, cls="icon"):
    return f'<span class="{cls}" aria-hidden="true">{get_svg(name)}</span>'

with open(os.path.join(base_dir, "_kw_data.json"), "r", encoding="utf-8") as f:
    KW_DATA = json.load(f)
try:
    with open(os.path.join(base_dir, "_kw_extra.json"), "r", encoding="utf-8") as f_extra:
        KW_EXTRA = json.load(f_extra)
except FileNotFoundError:
    KW_EXTRA = {}

# 读取文档
files = sorted([f for f in os.listdir(md_dir) if f.endswith(".md") and f != "slash-commands.md"])
docs_info = []
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
    desc = ""
    lines = content.split("\n")
    start = 0
    for i, line in enumerate(lines):
        if line.startswith("#"):
            start = i
            break
    for line in lines[start+1:]:
        line = line.strip()
        if line.startswith("#") or line.startswith(">") or line.startswith("<") or line.startswith("export"):
            continue
        if line:
            desc = line[:140]
            break
    if not desc:
        desc = "(无简介)"
    # 清理desc里的markdown链接
    desc = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', desc)
    size_kb = len(content.encode('utf-8')) / 1024
    docs_info.append({"name": f.replace(".md",""), "title": html_mod.escape(title), "desc": html_mod.escape(desc), "size_kb": size_kb})

print(f"文档总数: {len(docs_info)}")

# 文档卡片
doc_cards = ""
for d in docs_info:
    doc_cards += f'''<div class="doc-card" onclick="location.href='doc/{d['name']}.html'">
  <div class="doc-header">
    <span class="doc-title">{icon('file-text', 'doc-icon')}{d['title']}</span>
    <span class="doc-size">{d['size_kb']:.0f}KB</span>
  </div>
  <div class="doc-desc">{d['desc']}</div>
  <div class="doc-file">{d['name']}.md</div>
</div>\n'''

# 分类索引
categories = {
    "入门与基础": ["overview", "quickstart", "how-claude-code-works", "features-overview", "glossary", "best-practices", "common-workflows", "interactive-mode", "whats-new"],
    "CLI与命令": ["cli-reference", "commands", "keybindings", "settings", "env-vars", "statusline", "permission-modes", "permissions", "sessions", "context-window", "checkpointing"],
    "扩展体系": ["plugins", "discover-plugins", "plugins-reference", "plugin-marketplaces", "skills", "sub-agents", "hooks", "hooks-guide", "mcp", "mcp-quickstart", "agents", "agent-view", "agent-sdk_overview"],
    "工作流与自动化": ["workflows", "routines", "scheduled-tasks", "desktop-scheduled-tasks", "prompt-caching", "prompt-library", "memory", "code-review", "goal", "third-party-integrations"],
    "平台与集成": ["vs-code", "jetbrains", "desktop", "desktop-quickstart", "chrome", "slack", "platforms", "github-actions", "gitlab-ci-cd", "claude-code-on-the-web", "web-quickstart", "computer-use", "remote-control"],
    "部署与运维": ["setup", "admin-setup", "legal-and-compliance", "troubleshooting", "troubleshoot-install", "claude-directory", "zero-data-retention", "channels"],
}

index_html = ""
for cat, keys in categories.items():
    index_html += f'<h3 class="cat-title">{cat}</h3>\n<ul class="index-list">\n'
    for k in keys:
        for d in docs_info:
            if d['name'] == k:
                index_html += f'<li><a href="doc/{d["name"]}.html">{d["title"]}</a></li>\n'
                break
    index_html += '</ul>\n'

# 入门手册（md链接+emoji+关键词处理）
with open(os.path.join(base_dir, "Claude_Code扩展体系入门笔记.md"), "r", encoding="utf-8") as f:
    note_content = f.read()

EMOJI_MAP = {
    "📁": "folder", "🌿": "leaf", "💰": "coin", "🔗": "link", "👍": "thumb-up", "👎": "thumb-down",
    "🤖": "robot", "📊": "chart-bar", "⏱": "clock", "✅": "check", "❌": "x", "✗": "x", "✓": "check",
    "✽": "star", "✻": "star",
}

def replace_emoji(text):
    for e, sname in EMOJI_MAP.items():
        s = get_svg(sname)
        if s and e in text:
            text = text.replace(e, f'<span class="icon" aria-hidden="true">{s}</span>')
    text = text.replace("🔴", '<span class="dot dot-red"></span>')
    text = text.replace("🟡", '<span class="dot dot-yellow"></span>')
    text = text.replace("🟣", '<span class="dot dot-purple"></span>')
    return text

def convert_links(text):
    def repl(m):
        txt, url = m.group(1), m.group(2)
        if url.startswith("/docs/zh-CN/"):
            target = url.replace("/docs/zh-CN/", "").split("#")[0]
            anchor = "#" + url.split("#")[1] if "#" in url else ""
            if os.path.exists(os.path.join(md_dir, target + ".md")):
                return f'<a href="doc/{target}.html{anchor}">{txt}</a>'
            return f'<a href="https://code.claude.com/docs/zh-CN/{target}" target="_blank" rel="noopener">{txt}</a>'
        if url.startswith("/docs/"):
            return f'<a href="https://code.claude.com/docs{url}" target="_blank" rel="noopener">{txt}</a>'
        if url.startswith("http"):
            return f'<a href="{url}" target="_blank" rel="noopener">{txt}</a>'
        if url.startswith("#"):
            return f'<a href="{url}">{txt}</a>'
        if url.endswith(".md"):
            return f'<a href="doc/{url[:-3]}.html">{txt}</a>'
        return f'<a href="{url}">{txt}</a>'
    return re.sub(r'\[([^\[\]]+)\]\(([^()]+)\)', repl, text)

def md_to_html(md_text):
    lines = md_text.split("\n")
    out = []
    in_code = False
    in_table = False
    table_html = []
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
        if line.startswith("# "):
            out.append(f"<h2>{html_mod.escape(line[2:])}</h2>")
        elif line.startswith("## "):
            out.append(f"<h3>{html_mod.escape(line[3:])}</h3>")
        elif line.startswith("### "):
            out.append(f"<h4>{html_mod.escape(line[4:])}</h4>")
        elif line.startswith("> "):
            out.append(f"<blockquote>{html_mod.escape(line[2:])}</blockquote>")
        elif line.startswith("- "):
            li_text = html_mod.escape(line[2:])
            li_text = convert_links(li_text)
            li_text = replace_emoji(li_text)
            out.append(f"<li>{li_text}</li>")
        elif line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            is_sep = all(re.match(r'^:?-{2,}:?$', c) for c in cells)
            if not is_sep:
                def pc(cell):
                    cell = html_mod.escape(cell)
                    cell = convert_links(cell)
                    return replace_emoji(cell)
                if not in_table:
                    in_table = True
                    out.append("<div class='table-wrap'><table>")
                if table_html == []:
                    out.append("<tr>" + "".join(f"<th>{pc(c)}</th>" for c in cells) + "</tr>")
                else:
                    out.append("<tr>" + "".join(f"<td>{pc(c)}</td>" for c in cells) + "</tr>")
                table_html.append(line)
            continue
        elif line == "":
            if in_table:
                out.append("</table></div>")
                in_table = False
                table_html = []
            out.append("")
        else:
            escaped = html_mod.escape(line)
            escaped = convert_links(escaped)
            for kw in sorted(KW_DATA.keys(), key=lambda x: -len(x)):
                if kw in escaped:
                    escaped = escaped.replace(kw, f'<a class="kw" onclick="showKw(\'{kw}\')" title="点击查看解释">{kw}</a>')
            escaped = replace_emoji(escaped)
            out.append(f"<p>{escaped}</p>")
    if in_table:
        out.append("</table></div>")
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)

note_html = md_to_html(note_content)

# 更新日志
clog_html = '''
    <div class="card" id="changelog">
      <h2>{}更新日志</h2>
      <div class="clog-list">
        <div class="clog-item"><span class="clog-ver">v1.5</span><span class="clog-date">2026-08-05</span><span class="clog-desc">修复markdown链接转换、表格/列表链接遗漏、正文emoji全部SVG化、新增goal/hooks-guide/zero-data-retention文档</span></div>
        <div class="clog-item"><span class="clog-ver">v1.4</span><span class="clog-date">2026-08-05</span><span class="clog-desc">统一顶栏、错误汇报系统、更新日志、更新日期</span></div>
        <div class="clog-item"><span class="clog-ver">v1.3</span><span class="clog-date">2026-08-05</span><span class="clog-desc">98个专业词汇、关键词弹窗、雨云友情链接</span></div>
        <div class="clog-item"><span class="clog-ver">v1.2</span><span class="clog-date">2026-08-05</span><span class="clog-desc">64个独立阅读器页面、暗色主题、MDX组件转换</span></div>
        <div class="clog-item"><span class="clog-ver">v1.1</span><span class="clog-date">2026-08-05</span><span class="clog-desc">移动端适配、Tabler图标库</span></div>
        <div class="clog-item"><span class="clog-ver">v1.0</span><span class="clog-date">2026-08-05</span><span class="clog-desc">初始版本：官方中文文档+入门手册</span></div>
      </div>
    </div>
'''.format(icon('history'))

# 读取现有主页的CSS（复用）
with open(os.path.join(base_dir, "index.html"), "r", encoding="utf-8") as f:
    old_page = f.read()
m = re.search(r'<style>(.*?)</style>', old_page, re.S)
INDEX_CSS = m.group(1) if m else ""

# 读取汇报组件
with open(os.path.join(base_dir, "_report_components.txt"), "r", encoding="utf-8") as f:
    parts = f.read().split("@@SPLIT@@")
REPORT_CSS, REPORT_HTML, REPORT_JS = parts[0], parts[1], parts[2]

KW_JS_DATA = json.dumps(KW_DATA, ensure_ascii=False)
KW_JS_EXTRA = json.dumps(KW_EXTRA, ensure_ascii=False)

page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#0f1117">
<title>Claude Code 知识库</title>
<style>{INDEX_CSS}
{REPORT_CSS}
.clog-list {{ margin-top:10px; }}
.clog-item {{ display:flex; align-items:baseline; gap:12px; padding:8px 0; border-bottom:1px dashed var(--border); font-size:13.5px; }}
.clog-item:last-child {{ border-bottom:none; }}
.clog-ver {{ color:var(--accent); font-weight:700; flex-shrink:0; font-size:12px; background:var(--kw-bg); padding:2px 8px; border-radius:8px; }}
.clog-date {{ color:var(--muted); flex-shrink:0; font-size:12px; }}
.clog-desc {{ color:var(--text2); line-height:1.6; }}
.dot {{ display:inline-block; width:0.85em; height:0.85em; border-radius:50%; vertical-align:-0.1em; margin:0 2px; }}
.dot-red {{ background:#f03e3e; }} .dot-yellow {{ background:#f59f00; }} .dot-purple {{ background:#9c36b5; }}
</style>
</head>
<body>
<header class="topbar">
  <span class="logo">{icon('book')}Claude Code 知识库</span>
  <button class="hamburger" onclick="toggleDrawer()" aria-label="菜单">{icon('menu-2')}</button>
</header>
<aside class="drawer" id="drawer">
  <nav>
    <a href="#index" onclick="closeDrawer()">{icon('file-text')}文档索引</a>
    <a href="#changelog" onclick="closeDrawer()">{icon('history')}更新日志</a>
    <a href="#manual" onclick="closeDrawer()">{icon('book-2')}入门手册</a>
    <a href="#docs" onclick="closeDrawer()">{icon('file-text')}全部文档简介</a>
    <a href="#" onclick="closeDrawer();openRpt()">{icon('bug')}文档有误？汇报</a>
  </nav>
</aside>
<div class="overlay" id="overlay" onclick="closeDrawer()"></div>

<div class="container">
  <aside class="sidebar">
    <h2>{icon('book')}Claude Code 知识库</h2>
    <nav>
      <a href="#index">{icon('file-text')}文档索引</a>
      <a href="#changelog">{icon('history')}更新日志</a>
      <a href="#manual">{icon('book-2')}入门手册</a>
      <a href="#docs">{icon('file-text')}全部文档简介</a>
    </nav>
  </aside>
  <main class="main">
    <h1>Claude Code 知识库</h1>
    <p class="subtitle">官方中文文档（{len(docs_info)} 篇） + 入门手册 · 更新于 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} · 本地离线可用 · <span style="color:var(--accent2)">紫色虚线词 = {len(KW_DATA)}个专业词汇可点击解释</span></p>

    <div class="card" id="index">
      <h2>{icon('file-text')}文档索引</h2>
      <div class="search-wrap">
        {icon('search')}
        <input type="text" class="search-box" placeholder="搜索文档..." oninput="searchDocs(this.value)">
      </div>
      {index_html}
    </div>

    {clog_html}

    <div class="card" id="manual">
      <h2>{icon('book-2')}入门手册</h2>
      {note_html}
    </div>

    <div class="card" id="docs">
      <h2>{icon('file-text')}全部文档简介</h2>
      <p style="font-size:13px;color:var(--muted);">点击卡片打开完整文档阅读</p>
      <div id="doc-list">
        {doc_cards}
      </div>
    </div>
  </main>
</div>

<button class="scroll-top" id="scrollTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" aria-label="返回顶部">{icon('arrow-up')}</button>

<!-- 错误汇报弹窗 -->
<div class="rpt-overlay" id="rptOverlay" onclick="if(event.target===this)closeRpt()">
  <div class="rpt-modal">
    <div class="rpt-head">
      <span class="rpt-title">📮 文档有误？向服务器汇报！</span>
      <button class="rpt-close" onclick="closeRpt()">×</button>
    </div>
    <div class="rpt-body" id="rptForm">
      <div class="rpt-field">
        <label>问题页面</label>
        <div class="rpt-page" id="rptPage"></div>
      </div>
      <div class="rpt-field">
        <label>问题描述</label>
        <textarea id="rptDesc" placeholder="请描述你发现的问题：哪个词错了？哪里跳转不对？内容过时了？"></textarea>
      </div>
      <div class="rpt-field">
        <label>联系方式（选填）</label>
        <input id="rptContact" type="text" placeholder="QQ号 / 邮箱等，方便反馈处理结果">
      </div>
      <div class="rpt-tip">提交后内容会发送到服务器 reports/ 目录，管理员会尽快处理喵~</div>
      <button class="rpt-submit" id="rptBtn" onclick="submitRpt()">提交汇报</button>
    </div>
    <div class="rpt-ok" id="rptOk" style="display:none;">
      <div class="rpt-ok-icon">✅</div>
      <div class="rpt-ok-title">汇报成功！</div>
      <div class="rpt-ok-desc">感谢反馈，问题已记录到服务器</div>
    </div>
  </div>
</div>

<!-- 关键词弹窗 -->
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

<!-- 雨云友情链接 -->
<footer class="footer">
  <a href="https://www.rainyun.com/" target="_blank" rel="noopener">
    <div class="fy-badge">
      <div class="fy-logo">雨</div>
      <div class="fy-text">
        <div class="t1">本站由 雨云 提供计算服务</div>
        <div class="t2">开服开网站就选润雨云 · rainyun.com</div>
      </div>
    </div>
  </a>
</footer>

<script>
const KW_DATA = {KW_JS_DATA};
  const KW_EXTRA = {KW_JS_EXTRA};
let kwTimer = null;
function showKw(kw) {{
  const d = KW_DATA[kw] || KW_EXTRA[kw]; if (!d) return;
  document.getElementById('kwpBadge').textContent = kw;
  document.getElementById('kwpTitle').textContent = d.title;
  document.getElementById('kwpDesc').textContent = d.desc;
  var _kwpPfx = location.pathname.indexOf('/doc/') !== -1 || location.pathname.endsWith('/doc/') ? '' : 'doc/';
  document.getElementById('kwpLink').href = _kwpPfx + d.doc + '.html';
  const panel = document.getElementById('kwPanel');
  const estW = Math.min(480, Math.max(300, 280 + d.desc.length * 0.5));
  panel.style.width = estW + 'px';
  const dur = Math.min(14, Math.max(4, Math.round(d.desc.length / 55)));
  panel.classList.add('open');
  const bar = document.getElementById('kwBar');
  bar.style.transition = 'none'; bar.style.width = '100%';
  void bar.offsetWidth;
  bar.style.transition = 'width ' + dur + 's linear'; bar.style.width = '0%';
  clearTimeout(kwTimer);
  kwTimer = setTimeout(hideKw, dur * 1000);
}}
function hideKw() {{
  document.getElementById('kwPanel').classList.remove('open');
  clearTimeout(kwTimer);
}}
function toggleDrawer() {{
  document.getElementById('drawer').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('show');
}}
function closeDrawer() {{
  document.getElementById('drawer').classList.remove('open');
  document.getElementById('overlay').classList.remove('show');
}}
function searchDocs(q) {{
  q = q.toLowerCase();
  document.querySelectorAll('.doc-card').forEach(card => {{
    card.style.display = card.textContent.toLowerCase().includes(q) ? 'block' : 'none';
  }});
}}
window.addEventListener('scroll', () => {{
  document.getElementById('scrollTop').classList.toggle('show', window.scrollY > 400);
}});
{REPORT_JS}
</script>
</body>
</html>'''

with open(index_path, "w", encoding="utf-8") as f:
    f.write(page)
print(f"主页生成完成: {os.path.getsize(index_path)/1024:.1f}KB, 文档数: {len(docs_info)}")
