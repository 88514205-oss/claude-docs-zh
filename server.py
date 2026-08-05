#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claude Code 知识库服务器：静态文件 + 错误汇报接收"""
import http.server
import socketserver
import json
import os
import datetime
import s1g

BASE = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE, "reports")
PORT = 3333

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE, **kwargs)

    def end_headers(self):
        # S1g 相关接口允许跨域
        if self.path.startswith("/api/s1g"):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        if self.path.startswith("/api/s1g"):
            self.send_response(200)
            self.end_headers()
            return
        super().do_OPTIONS()

    def do_POST(self):
        if self.path == "/api/report":
            try:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length)
                data = json.loads(raw.decode("utf-8"))
                os.makedirs(REPORTS_DIR, exist_ok=True)
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                fname = f"report_{ts}.json"
                with open(os.path.join(REPORTS_DIR, fname), "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "id": fname}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
        elif self.path == "/api/s1g/ask":
            try:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length)
                data = json.loads(raw.decode("utf-8"))
                text = data.get("text", "")
                reply = s1g.ask(text)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"reply": reply}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/api/s1g/chat":
            try:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length)
                data = json.loads(raw.decode("utf-8"))
                text = data.get("text", "")
                history = data.get("history", [])
                reply = s1g.chat(text, history)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"reply": reply}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, fmt, *args):
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {fmt % args}")

S1G_CSS = None
S1G_JS = None

def _load_s1g():
    global S1G_CSS, S1G_JS
    css_path = os.path.join(BASE, "s1g.css")
    js_path = os.path.join(BASE, "s1g.js")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            S1G_CSS = f.read()
    if os.path.exists(js_path):
        with open(js_path, encoding="utf-8") as f:
            S1G_JS = f.read()

def inject_s1g(html):
    """向HTML注入S1g猫娘桌宠 + GitHub页脚"""
    if S1G_JS is None:
        return html
    css_tag = f"<style>{S1G_CSS}</style>"
    js_tag = f"<script>{S1G_JS}</script>"
    footer = (
        '<div class="s1g-footer">'
        '<div class="s1g-footer-title">🐾 CLAUDE CODE 中文知识库</div>'
        '<div>本项目开源 · <a href="https://github.com/88514205-oss/claude-docs-zh" target="_blank" rel="noopener">'
        'GitHub: 88514205-oss/claude-docs-zh</a></div>'
        '<div style="font-size:12px;color:#666;margin-top:6px;">Powered by S1g 猫娘助手 (・ω・)</div>'
        '</div>'
    )
    if "</body>" in html:
        html = html.replace("</body>", css_tag + js_tag + footer + "</body>", 1)
    else:
        html += css_tag + js_tag + footer
    return html

if __name__ == "__main__":
    os.makedirs(REPORTS_DIR, exist_ok=True)
    _load_s1g()
    print("[S1g] 猫娘助手已加载")
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    # 注入S1g到HTML响应
    _orig_do_GET = Handler.do_GET
    def _patched_do_GET(self):
        path_only = self.path.split("?")[0]
        is_html = path_only.endswith(".html") or path_only.endswith(".htm") or path_only in ("/", "/index.html")
        if not is_html:
            _orig_do_GET(self)
            return
        try:
            fs_path = self.translate_path(path_only)
            if os.path.isdir(fs_path):
                fs_path = os.path.join(fs_path, "index.html")
            if not os.path.isfile(fs_path):
                _orig_do_GET(self)
                return
            with open(fs_path, "rb") as f:
                content = f.read()
            html = content.decode("utf-8", errors="replace")
            html = inject_s1g(html)
            content = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except Exception:
            try:
                _orig_do_GET(self)
            except Exception:
                pass
    Handler.do_GET = _patched_do_GET
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"知识库服务器运行中: http://0.0.0.0:{PORT} (汇报目录: {REPORTS_DIR})")
        httpd.serve_forever()
