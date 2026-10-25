# AI职场沟通训练师 v5.0.18

v5.0.18 修复 Windows 启动脚本的编码/换行兼容性，显示打开进度和实际访问地址；保留全部分页对齐。

- `workplace-v5/`：可本地启动的 v4.18 改造副本；先读其中的 README.md 和 ACCEPTANCE.md。
- `handoff-source/`：上传交接包的原样文件，包含 original-v4.18、site-reference、visual-reference 及四份交接说明，源码摘要全部核对一致。

进入 `workplace-v5` 目录运行 `python server.py 8000`；Windows 可双击 start.bat，Linux/macOS 可用 bash start.sh。没有真实模型配置时不生成假对话。已有本机项目须通过 migrate_local.py 创建全新目录，保留原配置和历史。

本版新增页面底部自然语言输入与沟通经验库：可直接新建对象、补充画像和语录、调整强度、导入经验；原表单和历史保留。详细说明见 workplace-v5/README.md 的 v5.0.13 章节。

新增会议纪要导入（粘贴/TXT/Markdown/DOCX）：带原文依据提取对象观察、语录、项目背景和经验，按需核对保存，新训练可选择项目引用。见 workplace-v5/README.md 的 v5.0.14 章节。

会议纪要已移到自由输入区上方；公司模板成果展示 PPT、PDF 与逐页讲述稿位于 `presentation/`。

项目成果展示优先使用第七版：`presentation/AI-workplace-coach-story-v7.pptx`（31 页），封面后第 2 页嵌入 38.5 秒真实网页总览录屏，另附独立 MP4。保留第六版的对应布局和全部功能；API 接入为第 7 页，直接说输入/效果对照为第 23–26 页。详见 [展示材料说明](presentation/README.md)；旧版保留。
