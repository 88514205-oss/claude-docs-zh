# 🐾 Claude Code 中文知识库

![S1g](s1g.png)

**Claude Code 官方中文文档离线知识库** —— 爬取 [code.claude.com](https://code.claude.com) 官方文档，转成离线可读的暗色主题网站，内置 **S1g 猫娘 AI 助手**。

## ✨ 功能

- 📚 **64篇官方中文文档**，暗色主题阅读页（进度条、目录、翻页）
- 🟣 **98+ 专业词汇**紫色虚线高亮，点击弹抽屉解释
- 🐱 **S1g 猫娘桌宠**：
  - SVG 小猫娘，自由飘动，表情随速度方向变化（30+颜文字）
  - 可拖动，位置记忆，切换页面不重置
  - **划区提问**：划选网页内容，S1g 自动检索文档并回答
  - 打字机输出 + 思考状态栏（少女祈祷中…）
- 📝 **错误汇报系统**：读者可汇报文档错误到服务器
- 🖼️ 全站 SVG 图标，无 emoji 残留

## 🚀 快速启动

### 1. 环境要求
- Python 3.8+
- 一个 DeepSeek API Key（[获取](https://platform.deepseek.com)）

### 2. 配置 API Key（必读！）

本项目的 API Key **不会**内置在任何源码中，请自行配置：

```bash
# 第一步：复制示例配置
cp config.example.json config.json

# 第二步：编辑 config.json，填入你自己的 DeepSeek API Key
vim config.json   # 或任意编辑器
```

`config.json` 内容如下（`api_key` 必须换成你自己的）：

```json
{
  "deepseek": {
    "api_key": "sk-在这里填你自己的Key",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-v4-flash"
  }
}
```

> ### 🔐 安全说明
> - `config.json` 已被 `.gitignore` 忽略，**永远不会**被提交到 Git 仓库
> - 上传前请确认你的 `config.json` 没有被 `git add`（可用 `git status` 检查）
> - 如果误提交了密钥，请立即到 GitHub 仓库 Settings → Security → Rotate 更换 Key
> - 也可以改用环境变量方式：`export DEEPSEEK_API_KEY=sk-你的Key`（优先于 config.json）

### 3. 启动服务器

```bash
python3 server.py
# 或使用 systemd
systemctl start claude-docs
```

访问 `http://localhost:3333`

### 4. 重新生成文档页（可选）

```bash
python3 gen_reader.py   # 重新生成 64 个阅读页
python3 gen_index.py    # 重新生成主页
```

## 🗂️ 目录结构

```
├── server.py          # 服务器（静态页 + /api/report + /api/s1g/*）
├── s1g.py             # S1g 猫娘 AI 助手核心（检索 + LLM 回答）
├── s1g.js             # S1g 前端（飘动/拖动/划区提问/打字机）
├── s1g.css            # S1g 样式
├── doc_search.py      # 文档检索模块（md 切片 + 关键词）
├── config.example.json # API 配置示例（key 留空）
├── doc/*.html         # 64 个生成好的文档阅读页
├── md/*.md            # 原始官方中文文档
├── gen_reader.py      # 文档页生成脚本
├── gen_index.py       # 主页生成脚本
└── _kw_data.json      # 专业词汇弹窗数据
```

## 🐱 S1g 猫娘助手

S1g 是一只住在网站里的猫娘 AI 助手，专注解答 Claude Code 相关问题：

- **划区提问**：选中网页内容 → S1g 自动检索文档 → 回答
- **文档检索**：关键词提取 + 65 篇 md 切片索引
- **状态表情**：随飘动方向/速度变化，30+ 颜文字随机切换
- **思考状态**：正在ccb / 正在偷懒 / 少女祈祷中 / 正在加载 / 最上川！…

## 📝 更新日志

### v1.5
- 🐱 新增 S1g 猫娘 AI 助手（划区提问/文档检索/打字机/表情飘动）
- 🟣 关键词高亮颜色修正、补充词库（89 条）
- 🔧 修复 Tab/MDX 组件渲染、HTML 残留清理、锚点跳转

### v1.0
- 初始版本：64 篇文档 + 暗色阅读器 + 关键词弹窗 + 错误汇报

## 📄 许可

本项目仅供学习交流使用。Claude Code 官方文档版权归 Anthropic 所有。

---
🐾 Made with ❤️ by MasterKuma · [GitHub](https://github.com/88514205-oss)
