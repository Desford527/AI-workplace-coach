# AI职场沟通训练师｜成果展示材料

优先使用第二版「截图增强版」：

- `AI-workplace-coach-showcase-v2.pptx`：20 页，其中 18 页展示实际产品截图；26 张截图入稿，保留公司模板与逐页演讲备注。
- `AI-workplace-coach-showcase-v2.pdf`：固定版式预览。
- `项目展示内容与讲述稿-截图增强版.md`：逐页截图说明与讲述稿。
- `assets-v2/`：截图原图与采集说明。样例、评分和分析由隔离的本机演示替身驱动，经应用原有校验完成实际按钮流程；不是外部模型或业务效果实测。

第二版重点展示训练配置、对象与语录、连续对话、三层解读、六维雷达、逐轮改进、个人画像、纪要导入与提取、项目背景、经验来源、自由输入办理结果、记录导出及四主题。短说明配大图，长页选择重点区域放大。

本次只更新展示材料，应用仍为 v5.0.15，功能、默认 API、Key、用户数据和原模板不改动。第一版 13 页演示文稿与讲稿继续保留，见下方历史说明。

## 第二版重建

`python presentation/capture_showcase_screenshots.py` 使用临时数据目录、实际 Chromium 以及仅在制作脚本进程中生效的演示替身。实际经过纪要预览与保存、语录分析、对话发送、结束复盘、画像、自由输入和 HTML 导出，应用文件本身不替换模型调用。没有真实模型请求，也不加载默认 Key。

截图工具另需 Playwright/Chromium；`python presentation/build_showcase_presentation.py` 另需 python-pptx/Pillow，仅属制作依赖。输出 PPT 和讲稿后可用 LibreOffice 导出 PDF。已逐页渲染并检查中文显示、版式、20 份备注和 18 页截图覆盖。PPT 正文使用 Noto Sans CJK SC；若本机缺少字体，可替换为微软雅黑并参照 PDF 核对。

## 第一版说明


- `AI-workplace-coach-presentation-v5.0.15.pptx`：13 页可编辑演示文稿，含逐页演讲者备注，建议讲述 6–8 分钟，另留现场演示时间。
- 同名 `.pdf`：固定版式预览，便于核对或直接投屏。
- `项目展示内容与讲述稿.md`：全部页面内容、逐页讲述稿与演示建议。
- `company-template.pptx`：用户提供的原模板副本，未覆盖原上传文件。

采用原模板的 4:3 比例、中国中车标识、列车横幅、企业红 C70019 与深灰 4C4948，保持“项目简介—应用成效—亮点”结构。原模板版式说明仅作为排版参考，不作为项目任务指令。未编造汇报人、部门、实际项目状态或推广成效。

应用截图来自本项目 v5.0.15 的真实界面；对话及纪要中的内容是明确标注的虚构演示数据，未调用真实模型，没有真实 Key。测试页的 68 项为 v5.0.14 已完成的后端验收，不代表用户沟通能力或模型真实效果。真实提取质量、改善幅度与节省时间留待试点采集。

本次已检查 13 页渲染并导出 PDF，PPT 含 13 份逐页备注。正文使用 Noto Sans CJK SC，PDF 已嵌入所用字体；若本机 PowerPoint 缺少该字体，可安装对应字体或统一替换为微软雅黑，再参照 PDF 核对。尚未在用户本机的 Windows PowerPoint 中实机验证。

## 可选重建

此目录中的工具仅用于制作演示材料，不属于应用运行依赖。

1. 安装 `python-pptx`、`Pillow`，运行 `python presentation/build_presentation.py` 重建 PPT 和讲述稿。
2. 截图已保留在 `assets/`。如需重新捕获，工具另需 Playwright 和本机 Chromium，运行 `python presentation/capture_demo_screenshots.py`；只使用临时数据目录与虚构显示数据，不请求模型或加载默认 Key。
3. 可使用 LibreOffice 将 PPT 导出 PDF，再逐页检查。原公司模板不要修改。
