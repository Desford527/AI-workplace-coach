# AI 高压沟通教练（前端项目）

模拟难沟通的领导 / 导师，在连续追问与全盘复盘中提升高压沟通能力。
**前端选教练 + 填自己的大模型 API，由服务器把对应教练的 Skill 文件（`SKILL.md` + `references/*.md`）组装成 system prompt，再通过你的大模型驱动模拟答辩与答辩结果分析。**

## 目录结构

```
high-pressure-coach/
├─ index.html                 # 前端页面（单文件，含 CSS/JS）
├─ server.py                  # 本地服务器：托管静态页 + 组装 Skill + 持久化 API 配置
├─ skills/                    # 教练技能目录（标准 Skill 格式，每个教练一个子目录）
│  ├─ manifest.json           # 教练清单：显示哪些教练、默认是谁、场景与维度等展示元数据
│  ├─ zhangzong/              # 张总：SKILL.md + references/zhang-zong.md 人物档案 + 复盘框架
│  │  ├─ SKILL.md
│  │  └─ references/
│  │     ├─ zhang-zong.md     # 张总完整人物档案（模拟对话用）
│  │     ├─ coaching-framework.md  # 全盘复盘框架（答辩分析用）
│  │     └─ ...
│  └─ yanlaoshi/              # 严老师：同构，references/yan-laoshi.md
├─ user_data/                 # 本机隐私数据（API 配置 apiconfig.json，已被 .gitignore 忽略）
├─ CHANGELOG.md               # 修改记录：每次修改后必须在顶部追加一条记录
├─ start.bat / start.sh       # 一键启动
└─ README.md
```

## 运行方式（重要）

> 不要直接双击 `index.html`（file:// 协议下浏览器会拦截读取 skills/ 与调用 /api）。
> 必须通过本地服务器以 http 方式打开：

**Windows**：双击 `start.bat`
**macOS / Linux**：终端执行 `bash start.sh` 或 `python3 server.py`
**手动**：在本项目目录执行 `python server.py 8000`，浏览器打开 `http://localhost:8000`

### 打不开 / 提示"localhost 拒绝了我们的连接请求"？

通常是**本地服务器进程已退出**，端口只残留"僵死"监听。解决办法：

1. 确认服务器在运行：正常应有一个黑色窗口，里面打印 `AI高压沟通教练 已启动： http://localhost:8000`。
2. 若没有该窗口，重新启动：双击 `start.bat`（Windows）或执行 `python server.py 8000`。
3. 若仍打不开，说明端口被残留进程占着，先清掉再启动：
   - **Windows**：任务管理器 → 结束所有 `python` 进程；或命令行执行
     `netstat -ano | findstr :8000` 找到 LISTENING 的 PID，再 `taskkill /PID <pid> /F`，然后双击 `start.bat`。
4. **建议保持服务器常驻**：本页面依赖本地服务器，关掉它的终端窗口服务就会停。
   - 长期稳定使用：优先用打包好的 **`AI高压沟通教练.exe`**（双击即用，无需 Python）；
   - 或用独立窗口运行 `start.bat`，不要关那个窗口。

### 打包成 exe（对方电脑无需安装 Python）

在**有 Python 的电脑**上运行一次：

```
build_exe.bat        # Windows：自动装 PyInstaller 并生成 dist\AI高压沟通教练.exe
```

- 生成的是**单个 exe**（约 9MB），内置 `index.html` 与 `skills/`，对方**不需要装 Python**。
- 双击 exe 即启动本地服务并**自动打开浏览器**；关闭黑色窗口即停止。
- 用户的 API 配置保存在 **exe 同目录**的 `user_data\apiconfig.json`，便携可带走。
- 首次运行会解压到临时目录，需稍等 1–3 秒属正常。
- 设环境变量 `AHC_NO_OPEN=1` 可禁止自动打开浏览器。

## 使用步骤

1. 打开页面后，点右上角 **⚙ API**，管理多个 API：
   - **顶部下拉框**选择已保存的 API（没有则显示空白新建表单）；点 **「＋ 添加 API」** 新建。
   - 填写：**名称**（可选）、**API 地址（Base URL）**（如 DeepSeek 填 `https://api.deepseek.com`，自动补全 `/chat/completions`）、**API Key**、**模型**（下拉），勾选「用大模型生成对话」。
   - **「测试连接」** 校验当前表单（成功提示后请点「保存」生效）；**「保存」** 新增/覆盖并设为当前生效；**「删除」** 移除当前 API。
   - API 配置保存在本机 `user_data/apiconfig.json`（明文，含密钥，已 `.gitignore`）+ 浏览器 localStorage，不上传第三方。
2. 在「训练对象」选择教练（张总 / 严老师，来自 `skills/`），选场景，进入训练。
3. 像真实汇报一样回答，教练按其人设连续追问（由你的大模型生成，人设来自该教练的 Skill 文件）。
4. 点「结束并复盘」：雷达评分 + 失分点 + 高压话翻译表 + 时间线 + 示范回答 + 下一轮重点，并可导出独立 HTML 报告；配置大模型后，「教练总评 · AI」还会按 Skill 里的复盘框架生成总评。

> 模拟答辩必须配置大模型 API；未配置时页面会明确提示，不再有离线假对话。

## 如何新增 / 编辑 / 删除教练

**推荐直接用网页端**（字段与 skill 一致，自动写回对应文件，无需懂文件格式）：

- 训练对象区点「＋ 新增教练」创建；选中教练后点「✎ 编辑当前教练」修改（名称 / 头像字 / 身份 / 简介 / 主题色 / 回答结构提示 / 人设 / 场景+开场白 / 维度 / 难点 / 示范模板 / 语录）；「删除当前教练」移除（自定义整包删、内置可隐藏）。语录会在对话中自然使用。

下面保留**手动编辑 skill 文件**的方式（字段以 manifest 为准），适合批量操作或版本管理：

1. 在 `skills/` 下新建一个**标准 Skill 文件夹**，例如 `skills/li/`：
   - `SKILL.md`：该教练的完整技能设定（人设、追问逻辑、高压表达、复盘要求）。
   - `references/li-laoshi.md`：人物档案（模拟对话的 system prompt 会用到）。
   - `references/coaching-framework.md`：复盘框架（可复制现有教练的）。
2. 在 `skills/manifest.json` 的 `coaches` 数组里加一项，字段说明：

```jsonc
{
  "id": "li",                     // 唯一 id，与文件夹名对应
  "name": "李工",                  // 显示名
  "avatar": "李",                  // 头像字母
  "role": "技术型高压总监",          // 角色副标题
  "subtitle": "一句话介绍（卡片上显示）",
  "dir": "li",                    // skills/ 下的目录名
  "personaFile": "li-laoshi.md",  // references/ 下的人物档案文件名
  "scenes": [                      // 训练场景下拉项
    {"key": "周会汇报", "label": "周会汇报", "opening": "你汇报「{scene}」。说吧，结论是什么。"}
  ],
  "dims": [                        // 答辩分析的 6 个维度（顺序即雷达顺序）
    {"key": "结论清晰", "label": "结论清晰"},
    {"key": "数字支撑", "label": "数字支撑"},
    {"key": "工况覆盖", "label": "工况覆盖"},
    {"key": "设计依据", "label": "设计依据"},
    {"key": "边界风险", "label": "边界风险"},
    {"key": "应对追问", "label": "应对追问"}
  ],
  "dimNote": "结论—影响—根因—动作—请求",  // 维度说明小字
  "goodTemplate": "结论：[……]……",         // 示范回答“更强版本”模板
  "whyHard": "你为什么觉得难答……"           // 复盘里的“难答原因”文案
}
```

3. 刷新页面，新教练自动出现在训练对象列表，无需改前端代码。

### 大模型返回约定

为了让「高压话翻译表」正常工作，模拟对话要求模型**只返回 JSON**：

```json
{"line":"（教练这句追问原文）","surface":"表面在问什么","real":"真正关心什么","hidden":"隐藏判断标准"}
```

`server.py` 组装 `simulateSystem` 时已把这段约束写进 prompt；前端 `parseLLMJson` 会自动容错（剥离 ```json 代码块、截取括号），解析失败也保留大模型原文、不静默造假。

## 技术说明

- 纯静态前端，无构建步骤，无第三方 CDN。
- **Skill 驱动**：`server.py` 提供 `GET /api/coach/<id>`，读取该教练的 `SKILL.md` + `references/<personaFile>.md` + `coaching-framework.md`，组装成两套 system prompt：
  - `simulateSystem`（模拟对话，含 `{scene}` 占位，前端替换为所选场景）；
  - `analyzeSystem`（答辩总评，按复盘框架生成）。
- **对话**：前端把 `simulateSystem` 作为 system 消息、逐轮拼接历史，调用用户配置的 `/chat/completions`（不传 `max_tokens`，避免推理模型额度被思考链吃光导致 `content` 为空）。
- **分析**：数值评分由前端基于真实对话信号计算（非随机、可复现）；配置大模型后「教练总评 · AI」按 Skill 的复盘框架生成。
- 大模型调用失败时页面给出明确错误提示，不再回退到与 Skill 无关的离线假对话。
