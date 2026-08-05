#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claude Code 文档检索模块：md切片 + 关键词匹配"""
import os
import re
import json
import jieba
import math
import glob

BASE = os.path.dirname(os.path.abspath(__file__))
MD_DIR = os.path.join(BASE, "md")

class DocSearch:
    def __init__(self):
        self.docs = {}      # doc_name -> {title, sections: [{heading, text}]}
        self.load_all()

    def load_all(self):
        for fp in glob.glob(os.path.join(MD_DIR, "*.md")):
            name = os.path.basename(fp)[:-3]
            self.docs[name] = self._parse(open(fp, encoding="utf-8").read(), name)
        print(f"[S1g] 已加载 {len(self.docs)} 篇文档")

    def _parse(self, text, name):
        """按标题切分文档为小节"""
        # 清理HTML标签残留和MDX组件
        text = re.sub(r"</?[a-zA-Z][^>]*>", "\n", text)
        # 移除 export const JS代码块（官方交互组件残留）
        # 移除 export const JS代码块（括号匹配，兼容内含markdown示例的JS）
        def _strip_export_blocks(t):
            lines = t.split("\n")
            out = []
            i = 0
            while i < len(lines):
                if lines[i].strip().startswith("export const"):
                    depth = 0
                    started = False
                    j = i
                    while j < len(lines):
                        for ch in lines[j]:
                            if ch == "{":
                                depth += 1
                                started = True
                            elif ch == "}":
                                depth -= 1
                        if started and depth <= 0:
                            break
                        j += 1
                    i = j + 1
                    continue
                out.append(lines[i])
                i += 1
            return "\n".join(out)
        text = _strip_export_blocks(text)
        lines = text.split("\n")
        sections = []
        cur_heading = "概述"
        cur_text = []
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                if cur_text:
                    sections.append({"heading": cur_heading, "text": "\n".join(cur_text)})
                cur_heading = re.sub(r"^#+\s*", "", line)
                cur_text = []
            elif line:
                cur_text.append(line)
        if cur_text:
            sections.append({"heading": cur_heading, "text": "\n".join(cur_text)})
        return {"title": name, "sections": sections}

    def search(self, keywords, top_k=5):
        """按关键词检索（词频 × IDF），返回最相关的文档片段"""
        # 计算每个关键词的文档频率（IDF：越通用的词权重越低）
        df = {}
        for name, doc in self.docs.items():
            for sec in doc["sections"]:
                tl = sec["text"].lower()
                hl = sec["heading"].lower()
                for kw in keywords:
                    if not kw:
                        continue
                    if kw in tl or kw in hl:
                        df[kw] = df.get(kw, 0) + 1
        total_sections = sum(len(d["sections"]) for d in self.docs.values())
        idf = {}
        for kw in keywords:
            if not kw:
                continue
            idf[kw] = math.log(1 + total_sections / (1 + df.get(kw, 0)))

        results = []
        for name, doc in self.docs.items():
            for sec in doc["sections"]:
                score = 0
                text_lower = sec["text"].lower()
                heading_lower = sec["heading"].lower()
                hit_count = 0
                LOW_WEIGHT = {"agent": 0.15, "subagent": 0.15, "subagents": 0.15, "代理": 0.15, "claude": 0.25, "code": 0.25}
                for kw in keywords:
                    if not kw:
                        continue
                    c = text_lower.count(kw) * 2 + heading_lower.count(kw) * 5
                    if c > 0:
                        score += c * idf[kw] * LOW_WEIGHT.get(kw, 1.0)
                        hit_count += 1
                # 命中的关键词越多，相关性越强（AND倾向）
                score *= (1 + hit_count * 0.5)
                if score > 0:
                    # 围绕关键词首次命中位置截取上下文（避免关键内容被截断）
                    pos = -1
                    for kw in keywords:
                        if not kw:
                            continue
                        p = text_lower.find(kw)
                        if p > -1:
                            pos = p if pos == -1 else min(pos, p)
                    if pos > -1:
                        start = max(0, pos - 200)
                        snippet = sec["text"][start:start + 3000]
                        # 若命中"查看器/转录"等快捷键相关词但片段里没有具体快捷键，向后延伸找"Ctrl+"区域
                        if ("查看器" in snippet or "转录" in snippet) and "Ctrl+" not in snippet:
                            end_marker = sec["text"].find("Ctrl+", start + 1)
                            if end_marker > 0:
                                snippet = sec["text"][start:end_marker + 300]
                    else:
                        snippet = sec["text"][:600]
                    results.append({
                        "doc": name, "heading": sec["heading"],
                        "text": snippet, "score": score
                    })
        results.sort(key=lambda x: -x["score"])
        return results[:top_k]

    def extract_keywords(self, text, max_kw=5):
        """从文本中提取关键词（jieba分词 + 词频统计）"""
        text_clean = re.sub(r"[\s\[\](){}<>]+", " ", text)
        # 先剥离疑问词
        for q in ["怎么", "如何", "哪里", "什么", "为什么", "哪些", "哪个", "多少", "能否", "有没有", "是不是", "怎么办"]:
            text_clean = text_clean.replace(q, " ")
        words = []
        # 英文单词
        words += re.findall(r"[A-Za-z][A-Za-z0-9./_-]{1,}", text_clean)
        # 中文用 jieba 分词
        for seg in jieba.cut(text_clean):
            seg = seg.strip()
            if re.match(r"^[\u4e00-\u9fff]{2,}$", seg):
                words.append(seg)
        # 词频统计
        freq = {}
        for w in words:
            wl = w.lower()
            if len(wl) < 2:
                continue
            freq[wl] = freq.get(wl, 0) + 1
        # 排除常见停用词
        stop = {"claude", "code", "使用", "一个", "可以", "文档", "页面", "这个", "那个", "什么", "怎么", "为什么", "如何", "以及", "或者", "不是", "没有", "进行", "通过", "相关", "内容", "信息", "获取", "申请", "注册", "哪里", "多少", "哪些", "哪个", "需要", "应该", "能否", "有没有", "api", "key", "api key", "apikey", "密钥", "时候", "问题", "一下", "看看", "知道", "告诉"}
        ranked = sorted(freq.items(), key=lambda x: -x[1])
        kws = []
        for w, c in ranked:
            if w in stop:
                continue
            kws.append(w)
            if len(kws) >= max_kw:
                break
        # 同义词/相关词扩展（弥补语义鸿沟）
        SYNONYM_MAP = {
            "思考": ["transcript", "转录", "thinking", "查看器"],
            "显示": ["查看", "切换", "toggle", "transcript"],
            "查看": ["显示", "切换", "transcript"],
            "过程": ["transcript", "转录"],
            "安装": ["setup", "install", "troubleshoot"],
            "配置": ["setup", "settings", "config"],
            "快捷键": ["keybindings", "快捷键", "binding"],
        }
        expanded = list(kws)
        for kw in list(kws):
            for extra in SYNONYM_MAP.get(kw, []):
                if extra not in expanded:
                    expanded.append(extra)
        # 兜底：无有效关键词时用主题词
        if not expanded:
            expanded = ["claude"]
        return expanded[:max_kw + 3]

if __name__ == "__main__":
    ds = DocSearch()
    # 测试
    kws = ds.extract_keywords("如何配置 hooks 让代码在编辑后自动格式化？")
    print("关键词:", kws)
    for r in ds.search(kws):
        print(f"  [{r['score']}] {r['doc']} / {r['heading']}")
