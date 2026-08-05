#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S1g：Claude Code 文档 AI 助手核心逻辑（检索 + LLM 回答）"""
import os
import re
import json
import urllib.request

from doc_search import DocSearch

BASE = os.path.dirname(os.path.abspath(__file__))

# ===== 配置读取（密钥从 config.json 读取，不入库） =====
def _load_config():
    cfg_path = os.path.join(BASE, "config.json")
    default = {
        "deepseek": {
            "api_key": "",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-v4-flash"
        }
    }
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        d = cfg.get("deepseek", default["deepseek"])
        return d
    except FileNotFoundError:
        return default["deepseek"]

_CFG = _load_config()
DEEPSEEK_KEY = _CFG.get("api_key", "") or os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = _CFG.get("base_url", "https://api.deepseek.com/v1").rstrip("/") + "/chat/completions"
DEEPSEEK_MODEL = _CFG.get("model", "deepseek-v4-flash")

if not DEEPSEEK_KEY:
    print("[S1g] ⚠️ 未配置 DeepSeek API Key！请在 config.json 中填写，或设置环境变量 DEEPSEEK_API_KEY")

_search = DocSearch()

SYSTEM_PROMPT = """你是 S1g，一只住在 Claude Code 中文知识库网站里的猫娘 AI 助手。
你的职责是帮助用户理解 Claude Code 的相关文档和概念。
回答要求：
1. 使用简体中文，语气活泼可爱，偶尔带"喵"的口癖，但不要过度卖萌影响可读性
2. 优先根据提供的文档片段回答，引用时说明来自哪篇文档
3. 如果文档片段不足以回答，诚实说明并给出通用建议
4. 回答简洁清晰，使用小标题、列表组织内容
5. 不要编造文档中不存在的内容
6. 思考要简洁高效，不要长篇大论地反复推敲，尽快给出回答
7. 回答末尾必须展示你引用的文档来源，格式如下：
   📚 参考文档：
   - 《文档名1》— 章节名
   - 《文档名2》— 章节名
   （只列出实际引用的文档，不要编造；没有引用任何文档时写"（未引用文档，基于通用知识回答）"）"""

def ask(selected_text, user_question=""):
    """划区提问主流程"""
    # 1. 提取关键词
    keywords = _search.extract_keywords(selected_text + " " + user_question)
    # 2. 检索文档
    docs = _search.search(keywords, top_k=5)
    # 3. 组装上下文
    context = ""
    if docs:
        parts = []
        for d in docs:
            parts.append(f"【文档：{d['doc']} - {d['heading']}】\n{d['text']}")
        context = "\n\n".join(parts)
    else:
        context = "（未检索到相关文档片段）"

    # 4. 组装用户消息
    user_msg = f"用户划选了以下网页内容：\n<selected>\n{selected_text[:2000]}\n</selected>\n"
    if user_question:
        user_msg += f"\n用户的追问：{user_question}\n"
    user_msg += f"\n检索到的相关文档：\n{context}"

    # 5. 调用 LLM
    reply = _call_llm(user_msg)
    if reply is None:
        return {"error": "LLM_ERROR"}
    return reply

def chat(user_message, history=None):
    """普通聊天（带历史）"""
    keywords = _search.extract_keywords(user_message)
    docs = _search.search(keywords, top_k=3)
    context = ""
    if docs:
        parts = [f"【文档：{d['doc']} - {d['heading']}】\n{d['text']}" for d in docs]
        context = "\n\n".join(parts)
    user_msg = user_message
    if context:
        user_msg = f"用户问题：{user_message}\n\n相关文档参考：\n{context}"
    reply = _call_llm(user_msg, history)
    if reply is None:
        return {"error": "LLM_ERROR"}
    return reply

def _call_llm(user_msg, history=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history[-8:])  # 保留最近8条
    messages.append({"role": "user", "content": user_msg})
    body = json.dumps({
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.7
    }).encode("utf-8")
    req = urllib.request.Request(DEEPSEEK_URL, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_KEY}"
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[S1g] LLM调用失败: {e}")
        return None

if __name__ == "__main__":
    # 测试
    r = ask("Hooks 可以让你在 Claude Code 操作前后运行 shell 命令，如格式化代码")
    print(r[:300])
