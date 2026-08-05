#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claude Code 文档检索模块：md切片 + 关键词匹配"""
import os
import re
import json
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
        """按关键词检索，返回最相关的文档片段"""
        results = []
        for name, doc in self.docs.items():
            for sec in doc["sections"]:
                score = 0
                text_lower = sec["text"].lower()
                heading_lower = sec["heading"].lower()
                hit_count = 0
                for kw in keywords:
                    if not kw:
                        continue
                    c = text_lower.count(kw) * 2 + heading_lower.count(kw) * 5
                    if c > 0:
                        score += c
                        hit_count += 1
                # 命中的关键词越多，相关性越强（AND倾向）
                score *= (1 + hit_count * 0.5)
                if score > 0:
                    results.append({
                        "doc": name, "heading": sec["heading"],
                        "text": sec["text"][:600], "score": score
                    })
        results.sort(key=lambda x: -x["score"])
        return results[:top_k]

    def extract_keywords(self, text, max_kw=5):
        """从文本中提取关键词（简单规则：术语/长词/英文词优先）"""
        # 中文文档常见术语 + 英文术语
        text_clean = re.sub(r"[\s\[\](){}<>]+", " ", text)
        # 提取英文单词和中文长词
        words = re.findall(r"[A-Za-z][A-Za-z0-9./_-]{1,}|[\u4e00-\u9fff]{2,8}", text_clean)
        # 词频统计
        freq = {}
        for w in words:
            wl = w.lower()
            if len(wl) < 2:
                continue
            freq[wl] = freq.get(wl, 0) + 1
        # 排除常见停用词
        stop = {"claude", "code", "使用", "一个", "可以", "文档", "页面", "这个", "那个", "什么", "怎么", "为什么", "如何", "以及", "或者", "不是", "没有", "进行", "通过", "相关", "内容", "信息", "获取", "申请", "注册", "哪里", "多少", "哪些", "哪个", "需要", "应该", "能否", "有没有", "api", "key", "api key", "apikey", "密钥"}
        q_markers = ["怎么", "如何", "哪里", "什么", "为什么", "哪些", "哪个", "多少", "能否", "有没有", "是不是", "怎么办"]
        ranked = sorted(freq.items(), key=lambda x: -x[1])
        kws = []
        for w, c in ranked:
            if w in stop:
                continue
            # 过滤疑问词开头的词组（如"怎么获取"）
            if any(w.startswith(q) or q in w[:4] for q in q_markers):
                continue
            kws.append(w)
            if len(kws) >= max_kw:
                break
        # 兜底：无有效关键词时用主题词
        if not kws:
            kws = ["claude"]
        return kws

if __name__ == "__main__":
    ds = DocSearch()
    # 测试
    kws = ds.extract_keywords("如何配置 hooks 让代码在编辑后自动格式化？")
    print("关键词:", kws)
    for r in ds.search(kws):
        print(f"  [{r['score']}] {r['doc']} / {r['heading']}")
