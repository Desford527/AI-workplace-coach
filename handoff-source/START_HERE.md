# 给本机 Codex 的交接 · 2026-10-12

用户希望将 AI高压沟通教练 v4.18 改为 AI职场沟通训练师，保留原有 OpenAI 兼容 API 接口，使用真实模型训练与复盘。当前包是需求和源码交接，不是已完成的本地新版。

## 用户操作
1. 解压整个包到本机一个新文件夹，例如 D:\Projects\workplace-coach。
2. 在 Codex 桌面端选择该文件夹作为项目，粘贴 PROMPT_FOR_CODEX.txt 内容。
3. 若本机已有原项目及 API 配置，告诉 Codex 原项目位置；先保留原目录，用副本改造。不要把密钥粘贴到聊天。
4. 同一个账号不保证桌面 Codex 自动取得此聊天、文件、在线网站工具权限；此包为显式交接依据。

## 包内文件
- HANDOFF.md：完整产品要求、取舍、已知差异和验收清单。
- original-v4.18/：原始可运行 Python + 单 HTML 源码、教练 Skills、启动及打包脚本。API 配置已置为空，不包含旧 exe、嵌套 ZIP、运行 PID 和密钥。
- site-reference/：已上线网页的最新源码参考，包含六维 SVG 雷达图、规则评分及宽松布局。它是 Cloudflare Worker 项目，不能直接当作 Python 本地成品。
- visual-reference/previous-demo.html：用户认可美学的前任代理 HTML。它的回复与分析为规则，不是模型能力。
- SOURCE_MANIFEST.json：来源和源码摘要，帮助校验。
- AGENTS.md：给接手 Codex 的项目工作说明。

请优先阅读 HANDOFF.md，再逐个检查原代码。不要只据交接文档假定功能已经实现。
