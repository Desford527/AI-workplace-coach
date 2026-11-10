# 最新：第八版静态首页总览

[下载PPT](AI-workplace-coach-story-v8.pptx) · [PDF预览](AI-workplace-coach-story-v8.pdf) · [讲述稿](项目展示内容与讲述稿-第八版.md)

取消开场视频；背景介绍后，第5页用左右连续截图展示完整首页，再讲功能细节。

# AI职场沟通训练师｜成果展示材料

优先使用第七版「网页总览视频开场」：

- `AI-workplace-coach-story-v7.pptx`：31 页。封面后第 2 页嵌入 38.5 秒网页总览，放映时点击画面播放；视频随 PPT 保存，无需联网取外链。
- `video-v7/AI-workplace-coach-overview-v7.mp4`：可单独播放的 H.264 MP4，1280×816、30fps。为实际网页操作录屏，字幕放在网页画面下方，无配音。
- 视频依次展示首页、训练准备、连续对话、总分/六维复盘、对象画像、个人画像、经验库、会议纪要入口，以及直接说新增王工的实际结果。
- 同名 `.pdf` 只显示视频封面；`项目展示内容与讲述稿-第七版.md` 同步开场词、视频字幕及顺延后的页码。API 设置移至第 7 页，直接说四组对照移至第 23–26 页。
- 第六版主标题优先、目录与内容对应的布局继续保留；原各版文件、应用、默认 API 和用户数据不改动。
- `video-v7/manifest.json`、`overview.zh-CN.srt`、`overview.ass` 和 `poster.png` 记录视频时长、字幕、录制步骤及封面。详细验收和未实测项见 `STORY_V7_ACCEPTANCE.md`。

制作工具 `record_overview_video.py` 需要 Playwright/Chromium、录屏用 FFmpeg 及系统 FFmpeg（含 H.264/libass），在临时数据中使用演示替身，不请求真实模型或加载默认 Key。运行后用 `build_story_v7_presentation.py` 将 MP4 真正嵌入 PPT。制作依赖不属于应用运行依赖。

## 第六版说明

第六版「标题优先与页面对应」继续保留：

- `AI-workplace-coach-story-v6.pptx` / 同名 `.pdf`：保留第五版 30 页的功能、截图和顺序，主讲约 14 分钟。
- API 第 6 页去掉不对应的五标签目录；纪要、项目引用和四组自由输入页也去掉误挂的目录，改用对应入口说明，共移除 8 条不适用的目录。
- 其余 14 条目录保留实际选中状态，移到主标题下方。讲述顺序为重点文字 → 对应入口/页面目录 → 实际截图；产品全景截图本身的真实目录不改动。
- `项目展示内容与讲述稿-第六版.md`、`story-v6-content.json`：同步调整看图指向。`story-v6-layout.json` 记录各页目录处理，验收见 `STORY_V6_ACCEPTANCE.md`。
- 重建：`python presentation/build_story_v6_presentation.py`，基于已保留的第五版及其截图修改；不需重新调用模型或采集用户数据。本次没有修改应用、API 配置或历史。

## 第五版说明

第五版「功能完整展示与输入效果对照」继续保留：

- `AI-workplace-coach-story-v5.pptx` / 同名 `.pdf`：30 页，全部正常放映，主讲约 14 分钟。简介先背景和总体方案，第 5 页引入产品，第 6 页展示 API 接入，再进入训练案例。
- 第 6 页实际展示 API 配置名称、OpenAI 兼容服务地址及对话/复盘模型，使用无真实 Key 的 DeepSeek527 展示配置。展示 API 接入能力，不将本次截图表述为真实服务商连接测试。
- 第 22–25 页分别以“左边输入，右边实际效果”展示：新增王工、为朱总追加画像与语录、调整本轮和下次追问强度、把方法收录到经验库。右侧使用实际对象卡片、保存字段、训练状态及经验条目，不只展示办理回执。
- 画像、纪要提取和经验库改用更完整的截图范围，包含多项观察、人物/项目/经验条目、导入/导出/检索等入口；保留真实标签目录。对象表单维护、删除及四主题也进入主放映流程。
- `项目展示内容与讲述稿-第五版.md`、`story-v5-content.json`、`story-v5-coverage.json`：逐页讲稿、转场和完整功能页码表。
- `source-story-v4-user.pptx`：本次用户上传第四版的原样副本，封面与未涉及的页面保留。
- `assets-v5/`：本机隔离环境的真实 UI 截图、保存结果核对及采集说明。34 次演示替身调用均通过应用原有校验；3 场已复盘训练共 18 次回应，另有 1 场进行中训练用于强度调整演示。四组自然语言操作均刷新核对持久化结果。新采集截图使用 Asia/Shanghai 时区。
- 重建：`python presentation/capture_story_v5_screenshots.py`，然后 `python presentation/build_story_v5_presentation.py`。制作依赖沿用第四版；应用仍为 v5.0.18，原默认 API、配置与用户历史不变。详见 `STORY_V5_ACCEPTANCE.md`。

## 第四版说明

第四版「多轮画像与清晰评分」继续保留：

- `AI-workplace-coach-story-v4.pptx` / 同名 `.pdf`：26 页，24 页主讲；第 24、25 页默认隐藏，放映 1–23 → 26。主讲约 11 分钟，另留操作与提问时间。
- 第 9 页补入真实界面的总分卡（演示值 68 / 100）；第 10 页保留实际雷达截图，并从同一份复盘记录放大六维分数：72、64、58、74、68、72。
- 第 13–15 页展示三场训练、每场六轮、累计 18 次用户回应后的个人画像：摘要与沟通特征、已有优势与练习措施、三场原话及来源入口。
- `项目展示内容与讲述稿-第四版.md` / `story-v4-content.json`：按新页码整理的逐页讲稿与备注。
- `source-story-v3-user.pptx`：本次用户上传第三版的原样副本；在其基础上修订，保留用户对封面的调整，没有覆盖上传文件或旧版本。
- `assets-v4/`：48 张真实 UI 截图、经原有校验得到的复盘及画像数据、采集说明。使用隔离临时数据与只在制作进程中生效的本机演示替身，通过实际 UI 按钮完成三场训练、评分、画像更新及来源回看。分数及分析不代表真实模型或业务效果。
- 重建：先运行 `python presentation/capture_story_v4_screenshots.py`，再运行 `python presentation/build_story_v4_presentation.py`；依赖同第三版。PDF 导出需包含隐藏页。应用保持 v5.0.17，API 与历史不改动。
- 验收结果与未实测项见 `STORY_V4_ACCEPTANCE.md`。

## 第三版说明

第三版「案例讲述版」继续保留：

- `AI-workplace-coach-story-v3.pptx`：23 页，其中 21 页主讲，2 页备用且默认隐藏；逐页含重点、指图位置、讲稿、转场和建议时长。
- `AI-workplace-coach-story-v3.pdf`：固定版式预览，包含全部 23 页（含备用页）。
- `项目展示内容与讲述稿-第三版.md`：完整讲述稿和放映路线，主讲约 9–10 分钟，另留现场操作及提问时间。
- `assets-v3/`：35 张真实界面截图与采集说明。全景保留真实标签栏，细节放大页配对应分页的真实导航截图及选中状态，未重绘目录。
- `STORY_V3_ACCEPTANCE.md`：本版验收结果与未实测项。

第三版先用背景、问题、总体方案引入，简介只在最后一页出现产品截图；后续沿“向朱总汇报交付”同一案例展开：定目标 → 连续对话 → 理解追问 → 复盘改法 → 再练 → 纪要与画像、背景、经验积累 → 当前成果与下一步。对象管理与四主题移到备用页，避免打断主线。默认放映顺序为 1–20 页，然后自动跳到第 23 页结束。

本版截图仍使用隔离的本机演示数据；评分和分析不代表真实模型或业务效果。只更新展示材料，应用保持 v5.0.15，API 配置及用户数据不变。第一、二版及公司原模板均保留。

## 第三版重建

`python presentation/capture_story_screenshots.py` 在临时数据目录中运行真实 UI，使用只在制作进程中生效的演示替身，经应用原有校验完成按钮流程；不加载默认 Key、不请求外部模型。截图工具需要 Playwright/Chromium。

`python presentation/build_story_presentation.py` 使用 python-pptx/Pillow 生成 PPT、内容 JSON 与讲述稿。可用 LibreOffice 导出 PDF；需启用 `ExportHiddenSlides` 才会将备用页纳入 PDF。PPT 正文采用 Noto Sans CJK SC，PDF 嵌入字体；用户本机 Windows PowerPoint 尚未实测，可参照 PDF 核对版式。

## 第二版说明

第二版「截图增强版」继续保留：

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
