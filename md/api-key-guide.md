# 如何获取各个提供商的 API Key

本指南介绍如何注册并获取各大 AI 模型提供商的 API Key，用于配置 Claude Code、S1g 助手或其他 AI 应用。

> **通用流程**：注册账号 → 实名认证（国内服务商）→ 充值（部分）→ 创建 API Key → 复制保存

---

## DeepSeek（深度求索）

**官网**：https://platform.deepseek.com

| 步骤 | 操作 |
|:--|:--|
| 1 | 打开 platform.deepseek.com，用手机号注册 |
| 2 | 左侧菜单 → 「API Keys」→「创建 API Key」 |
| 3 | 填写名称（随意）→ 点击创建 |
| 4 | **立即复制保存**（关闭后不再显示完整 Key） |

- 模型：`deepseek-chat`（V3）、`deepseek-reasoner`（R1）
- 价格：约 ¥1~2 / 百万 token，新用户有免费额度
- 充值：控制台「充值」页面，支持支付宝/微信

---

## 硅基流动（SiliconFlow）

**官网**：https://siliconflow.cn

| 步骤 | 操作 |
|:--|:--|
| 1 | 注册账号（支持手机号/GitHub） |
| 2 | 左侧「API 密钥」→「新建 API 密钥」 |
| 3 | 复制生成的 `sk-...` 密钥 |

- 特点：聚合大量开源模型（Qwen、DeepSeek、GLM、Llama 等）
- 新用户注册送 14 元体验金
- 免费模型：部分模型可 0 元使用

---

## OpenAI（GPT）

**官网**：https://platform.openai.com

| 步骤 | 操作 |
|:--|:--|
| 1 | 注册 OpenAI 账号（需海外网络/手机号） |
| 2 | 登录后进入 platform.openai.com |
| 3 | 右上角头像 →「API keys」→「Create new secret key」 |
| 4 | 复制 `sk-...` 开头的 Key |

- 模型：`gpt-4o`、`gpt-4o-mini` 等
- 计费：按量付费，需绑定信用卡充值
- ⚠️ 国内直连不稳定，需要代理

---

## Anthropic（Claude）

**官网**：https://console.anthropic.com

| 步骤 | 操作 |
|:--|:--|
| 1 | 注册 Anthropic 账号 |
| 2 | console.anthropic.com →「API Keys」→「Create Key」 |
| 3 | 复制 `sk-ant-...` 开头的 Key |

- 模型：`claude-sonnet-4`、`claude-opus-4` 等
- 计费：按量付费，需海外信用卡
- ⚠️ 国内直连不稳定，需要代理

---

## Google Gemini

**官网**：https://aistudio.google.com

| 步骤 | 操作 |
|:--|:--|
| 1 | 登录 Google 账号 → aistudio.google.com |
| 2 | 左侧「Get API key」→「Create API key」 |
| 3 | 选择项目或新建 → 复制 Key |

- 模型：`gemini-2.5-pro`、`gemini-2.5-flash` 等
- 免费额度：Gemini Flash 系列有免费层
- ⚠️ 国内直连不稳定

---

## 通义千问（阿里云百炼）

**官网**：https://dashscope.aliyun.com

| 步骤 | 操作 |
|:--|:--|
| 1 | 用支付宝/淘宝账号登录阿里云 |
| 2 | 进入「百炼」（DashScope）控制台 |
| 3 | 右上角头像 →「API-KEY」→「创建新的 API-KEY」 |
| 4 | 复制 `sk-...` 开头的 Key |

- 模型：`qwen-max`、`qwen-plus`、`qwen-turbo`
- 新用户有免费额度
- 国内直连，无需代理

---

## 智谱 AI（GLM）

**官网**：https://open.bigmodel.cn

| 步骤 | 操作 |
|:--|:--|
| 1 | 注册智谱账号（手机号） |
| 2 | 登录后进入「API Keys」页面 |
| 3 | 「添加 API Key」→ 填写名称 → 创建 |
| 4 | 复制 `xxx.xxx` 格式的 Key |

- 模型：`glm-4-plus`、`glm-4-flash`（免费）
- 国内直连，新用户有体验额度

---

## 月之暗面（Kimi / Moonshot）

**官网**：https://platform.moonshot.cn

| 步骤 | 操作 |
|:--|:--|
| 1 | 注册 Moonshot 账号 |
| 2 | 控制台 →「API Key 管理」→「新建 API Key」 |
| 3 | 复制 `sk-...` 开头的 Key |

- 模型：`moonshot-v1-8k`、`kimi-k2` 等
- 超长上下文（200万汉字）
- 国内直连

---

## OpenRouter（聚合平台）

**官网**：https://openrouter.ai

| 步骤 | 操作 |
|:--|:--|
| 1 | 注册账号（Google/GitHub 登录） |
| 2 | 右上角头像 →「Keys」→「Create Key」 |
| 3 | 复制 Key |

- 特点：一个 Key 访问所有主流模型（Claude/GPT/Gemini/DeepSeek 等）
- 按量计费，支持充值

---

## 💡 通用注意事项

1. **Key 只显示一次**：绝大多数平台创建后只显示一次完整 Key，务必立即复制保存
2. **妥善保管**：Key 等同密码，不要发到公开场合（群聊/仓库/GitHub）
3. **限额管理**：建议在平台设置用量上限，防止被盗刷
4. **定期轮换**：怀疑泄露时立即在控制台删除并重建 Key
5. **Claude Code 配置**：获取 Key 后通过环境变量或 `~/.claude/settings.json` 配置，详见「使用第三方 API」章节

---

## 🔗 相关章节

* [快速开始](/docs/zh-CN/quickstart) — Claude Code 快速上手
* [使用第三方 API](/docs/zh-CN/quickstart#third-party-api) — 环境变量/配置文件接入方式
* [设置](/docs/zh-CN/settings) — 全局配置说明
