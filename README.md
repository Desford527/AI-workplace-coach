# AI职场沟通训练师 v5.0.13

- `workplace-v5/`：可本地启动的 v4.18 改造副本；先读其中的 README.md 和 ACCEPTANCE.md。
- `handoff-source/`：上传交接包的原样文件，包含 original-v4.18、site-reference、visual-reference 及四份交接说明，源码摘要全部核对一致。

进入 `workplace-v5` 目录运行 `python server.py 8000`；Windows 可双击 start.bat，Linux/macOS 可用 bash start.sh。没有真实模型配置时不生成假对话。已有本机项目须通过 migrate_local.py 创建全新目录，保留原配置和历史。

本版新增页面底部自然语言输入与沟通经验库：可直接新建对象、补充画像和语录、调整强度、导入经验；原表单和历史保留。详细说明见 workplace-v5/README.md 的 v5.0.13 章节。
