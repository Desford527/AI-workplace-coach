# AI职场沟通训练师 v5.0.15

- `workplace-v5/`：可本地启动的 v4.18 改造副本；先读其中的 README.md 和 ACCEPTANCE.md。
- `handoff-source/`：上传交接包的原样文件，包含 original-v4.18、site-reference、visual-reference 及四份交接说明，源码摘要全部核对一致。

进入 `workplace-v5` 目录运行 `python server.py 8000`；Windows 可双击 start.bat，Linux/macOS 可用 bash start.sh。没有真实模型配置时不生成假对话。已有本机项目须通过 migrate_local.py 创建全新目录，保留原配置和历史。

本版新增页面底部自然语言输入与沟通经验库：可直接新建对象、补充画像和语录、调整强度、导入经验；原表单和历史保留。详细说明见 workplace-v5/README.md 的 v5.0.13 章节。

新增会议纪要导入（粘贴/TXT/Markdown/DOCX）：带原文依据提取对象观察、语录、项目背景和经验，按需核对保存，新训练可选择项目引用。见 workplace-v5/README.md 的 v5.0.14 章节。

会议纪要已移到自由输入区上方；公司模板成果展示 PPT、PDF 与逐页讲述稿位于 `presentation/`。

项目成果展示优先使用第三版「案例讲述版」：`presentation/AI-workplace-coach-story-v3.pptx`（23 页，21 页主讲、2 页隐藏备用页），简介先讲背景和总体方案，后续以朱总交付汇报案例串联真实界面截图，截图保留实际标签导航。另附 PDF 与逐页讲述稿，详见 [展示材料说明](presentation/README.md)；旧版保留，应用版本保持 v5.0.15。
