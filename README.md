## 最新：PPT第十六版

[PPT](presentation/AI-workplace-coach-story-v16.pptx) · [PDF](presentation/AI-workplace-coach-story-v16.pdf)

发布页增加用户提供的项目说明原图，与仓库截图左右展示。

## 最新：PPT第十五版

[PPT下载](presentation/AI-workplace-coach-story-v15.pptx) · [PDF预览](presentation/AI-workplace-coach-story-v15.pdf)

36页：Skill视频按钮、实际GPT报告截图、倒数第二页GitHub、原感谢页结尾。

## 最新：PPT第十四版与可迁移Skill

[PPT](presentation/AI-workplace-coach-story-v14.pptx) · [PDF](presentation/AI-workplace-coach-story-v14.pdf) · [Skill下载](downloads/AI-workplace-coach-portable-skill-v1.0.zip) · [语音演示脚本](portable-skill/VOICE_DEMO.md)

## 最新：v5.1.2 / PPT第十三版

表达优化保留关键人物指代；第16页可选字段留空，并用大字展示优化结果。

[项目ZIP](downloads/AI-workplace-coach-v5.1.2.zip) · [PPT](presentation/AI-workplace-coach-story-v13.pptx) · [PDF](presentation/AI-workplace-coach-story-v13.pdf)

## 最新更新：v5.1.1 表达优化

新增「表达优化」标签，选择现有/通用对象，支持中文和英文输出；从情绪化原话整理合理工作诉求。

[新版应用ZIP](downloads/AI-workplace-coach-v5.1.1.zip) · [PPT第十二版](presentation/AI-workplace-coach-story-v12.pptx) · [PDF](presentation/AI-workplace-coach-story-v12.pdf)

## 最新更新：v5.1.0 海外客户与英语表达提升

项目启动与使用见 [workplace-v5/README.md](workplace-v5/README.md)，英文演示脚本见 [OVERSEAS_DEMO.md](workplace-v5/OVERSEAS_DEMO.md)。

[PPT第十一版](presentation/AI-workplace-coach-story-v11.pptx) · [PDF](presentation/AI-workplace-coach-story-v11.pdf)，第13–15页介绍海外英语沟通与语言提升。

# AI职场沟通训练师 v5.0.18

v5.0.18 修复 Windows 启动脚本的编码/换行兼容性，显示打开进度和实际访问地址；保留全部分页对齐。

- `workplace-v5/`：可本地启动的 v4.18 改造副本；先读其中的 README.md 和 ACCEPTANCE.md。
- `handoff-source/`：上传交接包的原样文件，包含 original-v4.18、site-reference、visual-reference 及四份交接说明，源码摘要全部核对一致。

进入 `workplace-v5` 目录运行 `python server.py 8000`；Windows 可双击 start.bat，Linux/macOS 可用 bash start.sh。没有真实模型配置时不生成假对话。已有本机项目须通过 migrate_local.py 创建全新目录，保留原配置和历史。

本版新增页面底部自然语言输入与沟通经验库：可直接新建对象、补充画像和语录、调整强度、导入经验；原表单和历史保留。详细说明见 workplace-v5/README.md 的 v5.0.13 章节。

新增会议纪要导入（粘贴/TXT/Markdown/DOCX）：带原文依据提取对象观察、语录、项目背景和经验，按需核对保存，新训练可选择项目引用。见 workplace-v5/README.md 的 v5.0.14 章节。

会议纪要已移到自由输入区上方；公司模板成果展示 PPT、PDF 与逐页讲述稿位于 `presentation/`。

项目成果展示优先使用第七版：`presentation/AI-workplace-coach-story-v7.pptx`（31 页），封面后第 2 页嵌入 38.5 秒真实网页总览录屏，另附独立 MP4。保留第六版的对应布局和全部功能；API 接入为第 7 页，直接说输入/效果对照为第 23–26 页。详见 [展示材料说明](presentation/README.md)；旧版保留。
