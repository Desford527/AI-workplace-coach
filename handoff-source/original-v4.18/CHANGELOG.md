# 修改记录（Changelog）

> **约定**：每次对项目文件做功能性修改后，必须在本文档**顶部**追加一条记录，包含：日期 / 版本 / 类型（新增·修改·修复·删除）/ 修改内容 / 涉及文件。
> 版本号规则：功能新增 +0.1；修复/优化 +0.0.1 级递增（以可读为准）。

---

## [v4.18] - 2026-08-10

### 修改（UI 优化）
- **API 弹窗底部同行**：「测试连接 / 取消 / 保存 / 删除」按钮与连接结果提示词放同一行（新增 `.apiFoot` 左右布局：左侧状态文字、右侧按钮），不再分两行。

### 涉及文件
- `index.html`

---

## [v4.17] - 2026-08-10

### 新增（解决"打不开 / 端口残留"）
- **exe 启动自愈**（`server.py`）：
  - **重复启动复用**：启动前先探测默认端口是否已在服务本应用（请求 `/api/manifest`）——是则直接打开浏览器并退出，避免双实例/双监听；
  - **端口自动顺延**：端口被占用或残留时自动顺延到下一个可用端口（最多 6 个），并把浏览器开到实际端口；`_can_bind` 不加 SO_REUSEADDR 以保证判断准确；
  - 记录 PID 文件（`user_data/server.pid`）便于排查。
- 已实测：干净启动 → 8000；重复启动 → 检测到已运行、自动退出、仍单监听；8000 被其它程序占用 → 自动切 8001 正常服务。

### 涉及文件
- `server.py`

---

## [v4.16] - 2026-08-10

### 修改（UI 优化）
- **弹窗操作按钮调矮并统一**：新增 `.modalActions button{padding:9px 16px;font-size:14px}`，弹窗内的「删除/测试/取消/保存」等按钮统一为更矮、协调的高度（约 40px），不再被 `.launch`/`.secondary` 的较大内边距拉高；页面其它按钮不受影响。

### 涉及文件
- `index.html`

---

## [v4.15] - 2026-08-10

### 修改（UI 优化）
- **两个弹窗底部间距收紧（不强行压矮）**：按钮到弹窗下边框的空隙主要由「状态行 apiStatus（min-height 16px + margin 10px）+ 底部内边距 20px」造成（约 46px），现改为：这两个弹窗底部内边距 `20px → 14px`、状态行 `margin-top:8px` 且空时不占高度，整体空隙约 22px，不紧不松。
- 高度上限由强制 `80vh` 改为安全兜底 `calc(100vh - 60px)`：不强行变矮窗口，仅在内容超高时保证不超出浏览器并内部滚动。

### 涉及文件
- `index.html`

---

## [v4.14] - 2026-08-10

### 修改（UI 优化）
- **两个弹窗降矮**：「编辑教练」与「API 管理」弹窗限高由 92vh 降至 **80vh**，避免超出浏览器；API 弹窗同样改为「标题/按钮固定 + 字段区内部滚动」（`apiCard` + `modalBody`）。

### 涉及文件
- `index.html`

---

## [v4.13] - 2026-08-10

### 修改（UI 优化）
- **仅「编辑教练」与「API 管理」弹窗加宽**：新增 `.modalCard.wide`（max-width 540px），只作用于这两个弹窗；基础 `.modalCard` 保持 460px，**网页整体宽度不变**（`.room` 仍 1240px，未改动）。

### 涉及文件
- `index.html`

---

## [v4.12] - 2026-08-10

### 修改（UI 优化）
- **弹窗统一加宽**：`.modalCard` 基础宽度 `460px → 540px`，「API 管理」与「教练编辑」弹窗同步变宽、保持一致（确认弹窗内联 360px 不受影响）。

### 涉及文件
- `index.html`

---

## [v4.11] - 2026-08-10

### 修改（UI 优化）
- **教练表单多行化**：「复盘维度」「为什么难答」「示范回答模板」由单行输入改为**多行文本框**（rows=3，`overflow-y:auto` 可内部滚动、可拖高），便于长内容显示。
- 复盘维度支持**每行一个**（换行解析），与逗号分隔兼容；编辑时回填按每行显示。

### 涉及文件
- `server.py`、`index.html`

---

## [v4.10] - 2026-08-10

### 修改（UI 优化）
- **教练弹窗加滚动**：编辑/新增教练窗口内容过长时，标题与「取消/保存」按钮固定，中间字段区在 `modalBody` 内滚动（`.modalCard.coachCard` 限高 92vh + `overflow-y:auto`）。

### 涉及文件
- `index.html`

---

## [v4.9] - 2026-08-10

### 修改（表单优化）
- **教练表单顶部字段同行**：「教练名称 / 头像字 / 主题色」放同一行（`coachRow` 三列布局），节省空间、便于对照。
- **必填校验**：教练名称与「身份 / 角色」为必填，缺任一则无法保存（前端提示 + 后端 `create_coach`/`update_coach` 双端校验）；其余字段选填。

### 涉及文件
- `server.py`、`index.html`

---

## [v4.8] - 2026-08-10

### 修改
- **移除独立的「管理语录」功能**：有了「编辑当前教练」后，语录管理并进教练表单——表单新增「语录 / 口头禅」字段（每行一句），新增/编辑时一并保存或清空。
- 删除了「✎ 管理语录」按钮、语录弹窗及其 CSS/JS（chips 增删逻辑）；后端 `get_quotes/set_quotes` 与 `/api/quotes/<id>` 保留，`create_coach`/`update_coach` 现直接处理 `quotes` 字段。
- README 同步更新。

### 涉及文件
- `server.py`、`index.html`、`README.md`

---

## [v4.7] - 2026-08-10

### 修改（文档）
- **README 补充故障处理**：新增「打不开 / localhost 拒绝了连接请求？」一节（原因：本地服务器进程退出、端口残留僵死监听；解决：确认/重启服务器、清残留进程、建议用 exe 或常驻 start.bat）。
- README「如何新增一位教练」改为「如何新增 / 编辑 / 删除教练」，**推荐网页端操作**（＋ 新增 / ✎ 编辑 / 删除 / 管理语录），手动编辑 skill 文件保留为备选。

### 涉及文件
- `README.md`

---

## [v4.6] - 2026-08-10

### 修改（网页端字段与 skill 对齐）
- **表单字段补全到与 skill/manifest 一致**：新增/编辑表单新增「回答结构提示（dimNote）」字段；「训练场景」由单行改为**多行文本框，支持每行「场景名：开场白」自定义开场白**（对应 manifest 中 scenes[].opening，`{scene}` 占位符自动替换）。
- `server.py`：新增 `parse_scenes()`/`parse_dims()`（兼容字符串与结构化数组），`create_coach`/`update_coach` 统一使用并写入 `dimNote`。
- 现在新增/编辑可操作字段 = manifest 全部教练字段（name/avatar/role/subtitle/color/dimNote/scenes+opening/dims/whyHard/goodTemplate）+ 人设（persona）+ 语录（quotes 独立弹窗）。

### 涉及文件
- `server.py`、`index.html`

---

## [v4.5] - 2026-08-10

### 新增（功能）
- **编辑教练**：训练场新增「✎ 编辑当前教练」按钮；新增与编辑共用同一表单（字段统一：名称 / 头像字 / 身份 / 简介 / 主题色 / 人设 / 场景 / 维度 / 难点 / 示范模板），编辑时自动回填当前值。
- **内容与 skill 保持一致**：编辑保存时同步改写对应 skill 文件——人设 → `references/<personaFile>.md`（可写覆盖，内置教练也生效），其余字段 → manifest 条目（同 id 覆盖）；自定义教练同时重建 SKILL.md。
- `server.py`：新增 `update_coach()` 与 `POST /api/coach/update`；`assemble_coach` 返回 `persona` / `personaFile` 供表单回填。
- 已测试：自定义教练编辑（改名/人设/场景/维度）、内置教练重命名（simulateSystem 与新名字/新人设一致）均通过；HTTP update 不存在教练 400 无副作用。

### 涉及文件
- `server.py`、`index.html`

---

## [v4.4] - 2026-08-10

### 新增（功能）
- **删除教练**：
  - 训练场设置区新增「删除当前教练」按钮（红色），确认弹窗后删除。
  - 自定义教练（`c_*`）：整包删除 `skills/<id>/` 目录、语录文件与清单条目（不可恢复）。
  - 内置教练：加入 `skills/deleted.json` 隐藏清单（skill 文件保留，删除该文件中的条目即可恢复）。
  - `server.py` 新增 `do_DELETE /api/coach/<id>` 与 `delete_coach()`；`load_manifest` 过滤隐藏教练。
- 已测试：自定义教练创建→删除（目录/清单清理）、内置隐藏→恢复；HTTP DELETE 冒烟（不存在教练返回 400 无副作用）。

### 涉及文件
- `server.py`、`index.html`

---

## [v4.3] - 2026-08-10

### 修复
- **打开页面未自动检测已有教练**：根因是服务器未响应（端口残留僵死进程），`/api/manifest` 加载失败导致教练区为空。
  - `loadSkills` 增加兜底：`/api/manifest` 失败时自动退回静态 `skills/manifest.json`，确保打开页面一定能自动检测到内置教练（旧服务器/接口异常也不影响）。

### 涉及文件
- `index.html`

---

## [v4.2] - 2026-08-10

### 修复
- **发送消息按钮无法发送（严重 bug）**：发送函数 `send` 与表单内控件 `id="send"` 同名。表单内联事件处理器的作用域链会优先把 `send` 解析为"表单里名为 send 的控件"（按钮本身），导致点击报 `send is not a function`、消息发不出去。已把全局函数改名 `sendMsg`（`onclick` 与 Enter 发送同步更新）。
- 已用无头浏览器（Edge + CDP）实测：进入训练 → 输入 → 点击发送 → 消息上屏、真实调用大模型并收到教练追问，无任何报错。

### 修改（UI）
- 训练场「进入训练 ↗」按钮下移：新增 `#begin{margin-top:16px}`，与场景下拉留出间隔。

### 涉及文件
- `index.html`

---

## [v4.1] - 2026-08-10

### 新增（功能）
- **教练语录管理**：
  - 训练场设置区新增「✎ 管理语录（当前教练）」按钮 → 弹窗增删语录（chips 可删除、输入框可添加），保存即生效；教练卡片展示前 3 条口头禅。
  - `server.py`：`get_quotes/set_quotes`（语录存可写覆盖文件 `skills/quotes/<id>.json`，exe 场景存 exe 旁，内置+覆盖合并去重）；新增 `GET/POST /api/quotes/<id>`；`simulateSystem` 注入「口头禅 / 语录」段（要求自然使用、不堆砌）。
  - 已端到端验证：保存张总 3 条语录 → simulateSystem 含语录段与内容、coach.quotes 返回正常，测试数据已清理。

### 涉及文件
- `server.py`、`index.html`

---

## [v4.0] - 2026-08-10

### 新增（功能）
- **新增教练功能**：
  - 训练对象区新增「＋ 新增教练」虚线卡片 → 弹窗填写名称 / 身份 / 简介 / 人设 / 场景 / 复盘维度 / 难点 / 示范模板，一键创建并立即生效。
  - `server.py`：新增 `GET /api/manifest`（合并内置 + 自定义教练清单）、`POST /api/coach`（写入 `skills/<id>/SKILL.md`、`references/custom-persona.md`、复盘框架并登记清单）。自定义教练在 exe 场景下写入 exe 旁 `skills/`（可写目录优先读取）。
  - 前端 `loadSkills` 改走 `/api/manifest`；教练卡片 / 角色按钮 / 场景选项对用户文本做 HTML 转义（防注入）。
- 已端到端验证：POST 创建「李总」→ 清单出现、`/api/coach/<id>` 正常组装（含角色锁定规则），测试数据已清理干净。

### 涉及文件
- `server.py`、`index.html`

---

## [v3.9] - 2026-08-10

### 修改
- **打包脚本完善**：`build_exe.bat` 打包成功后，自动把 `dist\AI高压沟通教练.exe` **复制到项目根目录**，并清理全部临时文件（`build\`、`dist\`、`AI高压沟通教练.spec`、`__pycache__`），最终只留根目录的 `AI高压沟通教练.exe`；构建失败则保留临时目录便于排查。

### 涉及文件
- `build_exe.bat`

---


### 修改
- **打包后自动清理临时文件**：`build_exe.bat` 打包成功后自动删除 `build\` 目录、`AI高压沟通教练.spec` 与 `__pycache__`，仅保留 `dist\AI高压沟通教练.exe`；构建失败时提示先删 `build` 再试。
- 已手动清除本次打包残留（`build` / `build_tmp` / `dist` / `dist2` / `__pycache__` / `.spec` / 校验用 `venv_check`），项目根目录只保留交付文件。

### 涉及文件
- `build_exe.bat`

---


### 新增（打包发布）
- **支持打包为单文件 exe（对方无需安装 Python）**：
  - `server.py` 兼容 PyInstaller 冻结模式：静态资源（index.html/skills/）从内置 `_MEIPASS` 读取；用户配置写入 **exe 同目录** `user_data/apiconfig.json`（便携）；exe 启动自动打开浏览器（`AHC_NO_OPEN=1` 可禁止）。
  - 新增 `build_exe.bat`（自动装 PyInstaller 并生成 `dist\AI高压沟通教练.exe`）。
  - 已实测构建：9MB 单文件 exe，首页 / 教练接口 / manifest / 配置接口均 200，无 Python 环境可用。

### 涉及文件
- `server.py`、`build_exe.bat`、`README.md`

---


### 修改（UI 调整）
- 训练房间头部身份区排版：教练名称与「场景 · 训练进行中」由挤在同一行改为**分行显示并留出间距**（`.identity b/small` 设 `display:block` + `margin-top`），严老师、张总同理。

### 涉及文件
- `index.html`

---


### 修改（UI 调整）
- 训练房间头部按钮不再挤：新增 `.trainBtns` 右对齐按钮组（flex + gap），「中断训练」与「结束并复盘」统一收纳；`.training header` 支持换行，窄屏下按钮组自动折行到下一行；两按钮内边距微调。

### 涉及文件
- `index.html`

---


### 新增
- **随时中断训练**：训练房间头部新增琥珀色「中断训练」按钮，与「结束并复盘」并列；点击弹出确认框（不生成复盘、清空对话），确定即返回主界面，取消继续对话。新增 `.abort` 按钮样式与 `abortTraining()`。

### 涉及文件
- `index.html`

---


### 修改
- **对话模型 / 复盘模型下拉框格式统一**：复盘模型由「文本输入 + datalist」改为与对话模型一致的 `<select>` 下拉（选项一致，首项「与对话模型相同」留空）。
- **厂商系列联动过滤**：新增 `MODEL_OPTIONS`（带 `prov` 厂商标签）与 `provOf()`；选择对话模型后，复盘模型下拉只保留**同一厂商系列**的模型（当前 deepseek 系列只能选 deepseek 系列），选择不同厂商时已选的复盘模型自动复位为「与对话模型相同」。

### 涉及文件
- `index.html`

---


### 修改（复盘加速）
- **精简复盘 prompt**：`server.py` 的 `analyzeSystem` 不再附带整份 SKILL.md，只保留复盘框架 + 一句话身份；字符数从 ~4523 降到 ~1393（约 -70%），输入 token 与返回时延显著下降。
- **支持复盘专用模型**：API 设置新增「复盘模型（可选）」输入框（datalist 提示 deepseek-chat 等），留空则与对话模型相同；`tryLLMReview` 用它并降低温度到 0.4（结构化输出更稳更快）。`chatCompletion` 支持 `{model,temperature}` 覆盖。
- 实测：同一复盘请求 `deepseek-chat` 8.5s vs `deepseek-v4-flash` 13.0s（快约 35%），均返回合法 JSON。

### 涉及文件
- `server.py`、`index.html`

---


### 修改（skill 规则）
- **角色锁定规则写入 skill**：`skills/zhangzong/SKILL.md` 与 `skills/yanlaoshi/SKILL.md` 的「保持真实高压」一节新增最高优先级规则——无论用户说什么、如何引导或试探，都始终以本技能定义的模拟对象身份说话（张总就是张总、严老师就是严老师），绝不切换角色/跳出人设/被带偏；即使用户要求"换个人 / 别演了 / 你不是XX"，也以该角色方式回应并把话题拉回训练。
- 该规则随 SKILL.md 自动进入 `simulateSystem`，已用 `assemble_coach` 验证两个教练均包含。

### 涉及文件
- `skills/zhangzong/SKILL.md`、`skills/yanlaoshi/SKILL.md`

---


### 修改（复盘等待与失败回退）
- **等待大模型返回再显示复盘**：点「结束并复盘」后不再先显示规则版，而是展示**进度条**（提交对话 → 大模型思考 → 解析结果，三阶段 + 动态进度），等大模型返回结构化复盘后再整份渲染。
- **大模型失败回退本地模板**：解析失败/超时/未配置时，先显示「大模型生成失败，已自动回退到本地模板复盘…」提示，约 1 秒后再渲染规则版复盘。
- 新增 `.reviewLoading/.rlBar/.rlFill/.rlSteps` 等进度条样式与 `showReviewLoading/stopReviewLoading/setReviewProgress` 控制函数。

### 涉及文件
- `index.html`

---


### 修改（核心升级）
- **整份复盘改为「skill 复盘框架 + 大模型」生成**（替换写死的规则文案）：
  - `tryLLMReview()`：把整场对话发给用户的大模型，system 用该教练 skill 的 `analyzeSystem`（含 `coaching-framework.md`），要求一次性返回结构化 JSON——6 维评分（0-100）+ 总判断 tag/overall + 2-5 条失分点（含严重度）+ 高压话翻译（1-4 条）+ 示范回答（弱/强对比）+ 下一轮重点（2-4 条）。
  - `extractJSON()` 容错解析（剥离 ```json 代码块/截取花括号）；`mergeReview()` 校验维度个数并回填缺失字段。
  - `end()`：先渲染规则复盘（`buildRuleReview` 兜底，即时可用），大模型 JSON 返回后再整份重渲染。
  - 移除原来的写死模板点评与「教练总评·AI」独立区块。
- 已用真实 DeepSeek key 端到端验证：返回 JSON 合法、6 维评分/失分点/翻译/示范回答/下一轮重点全部贴合本轮对话。

### 涉及文件
- `index.html`

---


### 修改
- **无对话结束提示改为页面内弹窗**：新增自定义确认弹窗（`#confirmModal`，复用 `.modal/.modalCard` 风格），替代浏览器原生 `confirm`。无对话点「结束并复盘」时弹出，确定返回主界面、取消继续对话。

### 涉及文件
- `index.html`

---


### 修改
- **API 保存后不再自动关闭设置弹窗**：保存成功给出提示并保持弹窗打开，方便继续新增/切换 API（手动点关闭或「取消」退出）。
- **无对话也能「结束并复盘」**：未开始对话时点击「结束并复盘」弹出确认框；确定则返回主界面（不生成复盘），取消则继续对话。`change()` 同时隐藏训练房间，保证从任意状态都能回到主界面。

### 涉及文件
- `index.html`

---


### 修改（UI 优化）
- API 管理弹窗整体压矮：卡片内边距、输入框高度、标签间距、按钮边距、编辑区/状态栏间距均微调缩小；下拉箭头纵向位置同步微调。
- 弹窗提示文案去掉「（user_data/apiconfig.json + 浏览器）」存储位置说明，简化为「Key 仅保存在本机，不上传任何第三方。」

### 涉及文件
- `index.html`

---


### 修改（修复）
- 对话气泡与打字指示器中的教练称呼修正：原先拼成「张总/张老师」「严总/严老师」，现直接使用教练名称——张总只显示「张总」、严老师只显示「严老师」（`botSay` / `typing` 改为 `state.coach.name`）。

### 涉及文件
- `index.html`

---


### 修改（重构）
- **多 API 管理**（参考 Cline 的添加逻辑）：
  - 弹窗顶部新增「已保存 API」下拉框：选择即载入该 API；没有任何 API 时直接显示空白新建表单。
  - 「＋ 添加 API」按钮打开全新空白表单；表单字段：名称（可选）/ Base URL / Key / 模型下拉 / 用大模型生成对话。
  - 「保存」：新增或覆盖当前编辑的 API，并设为当前生效；「删除」：删除当前 API（若编辑的是未保存草稿则清空表单）。
  - 「测试连接」仅校验当前表单内容，成功后提示点「保存」生效。
- 存储结构升级为 `{apis:[{id,name,baseURL,apiKey,model,useLLM}], active}`（localStorage + `user_data/apiconfig.json`）；旧版单配置格式打开时自动迁移，不丢数据。
- 页面状态栏显示当前生效 API 名称。

### 涉及文件
- `index.html`、`README.md`

---


### 新增
- 新增本修改记录文档 `CHANGELOG.md`，并约定后续每次修改后必须在此追加记录。

### 涉及文件
- `CHANGELOG.md`（本文件）

---

## [v2.2] - 2026-08-10

### 修改 · 新增
- **API 设置界面优化**：
  - 新增「删除已有 API」按钮：确认后清空浏览器 `localStorage` + 内存配置，并 `POST {}` 覆写本机 `user_data/apiconfig.json`，重置表单并刷新状态栏；无配置时按钮置灰。
  - 保留「添加/更新」能力：保存按钮改为「保存 / 添加」，测试连接成功仍自动保存。
  - 弹窗顶部新增「已保存配置」摘要框（Base URL · 模型 · Key 打码 · 对话开关），绿点=已保存、黄点=未保存。
  - 表单 Key 输入框加 `autocomplete="new-password"`，按钮区支持换行。
- 更新 README 使用说明（删除/添加流程）。

### 涉及文件
- `index.html`、`README.md`

---

## [v2.1] - 2026-08-10

### 修改
- **API 超时自动重连**：
  - 对话请求超时/空返回时自动重连，最多重试 2 次（每次全新 fetch），重连期间打字指示器显示「连接超时，正在自动重连…（第N次）」。
  - 失败/超时产生的占位气泡不再计入对话历史，保证下一次回复是干净重连。
  - AI 总评（`enrichReview`）超时自动重连 1 次。
  - 新增 CSS `.typing .note`（琥珀色重连提示）。

### 涉及文件
- `index.html`

---

## [v2.0] - 2026-08-09

### 修改（重构）
- **Skill 驱动架构**：教练定义从旧 `coach.json` 改为标准 Skill 目录 `skills/zhangzong`、`skills/yanlaoshi`（每个含 `SKILL.md` + `references/`：`zhang-zong.md`/`yan-laoshi.md` 人物档案、`coaching-framework.md` 复盘框架）。
- `server.py` 新增 `GET /api/coach/<id>`：读取该教练 Skill 文件，组装 `simulateSystem`（模拟对话 prompt）与 `analyzeSystem`（复盘总评 prompt），并去掉 YAML frontmatter。
- `index.html`：删除内置规则引擎与 `BUILTIN`；教练从 `/api/coach/<id>` 动态加载；模拟答辩与分析均由 Skill + 用户大模型驱动；未配 API 时明确提示、不伪造对话。
- `skills/manifest.json` 重构为对象数组（id/name/avatar/role/subtitle/dir/personaFile/scenes/dims 等），默认教练 `zhangzong`。

### 修复
- 严老师（张总同理）此前不连大模型的根因：推理模型 + 限制 `max_tokens` 导致 `content` 为空 → 静默回退规则引擎。已去掉 `max_tokens`、`parseLLMJson` 增加兜底保留原文。

### 涉及文件
- `index.html`、`server.py`、`skills/manifest.json`、`README.md`；删除 `skills/zhang`、`skills/yan`（旧 coach.json 格式）

---

## [v1.4] - 2026-08-09

### 修改 · 修复
- **API 配置持久化到本机文件**：`server.py` 新增 `GET/POST /api/config`，配置保存到独立 `user_data/apiconfig.json`；打开页面自动读取回填。
- **用户反馈修复**：
  - 测试连接成功即自动保存（`testApi` 成功后 `saveApiRaw+persistServer+updateApiInfo`），避免忘点保存导致仍显示「未配置」。
  - `chatCompletion` 超时 20s → 60s（推理模型 + 长 prompt 常超时）；失败 toast 区分超时/其他。
  - `saveApiRaw`/`loadServerConfig` 归一化 `useLLM`（缺省 true）；状态栏「未配置」文案更新。

### 涉及文件
- `server.py`、`index.html`、`README.md`、`user_data/.gitignore`

---

## [v1.3] - 2026-08-09

### 修改
- **API 登录界面模型改为下拉框**：默认 `deepseek-v4-flash`，备选 `deepseek-v4-pro` / `deepseek-chat` / `deepseek-reasoner`；Base URL 占位符改为 DeepSeek 官方地址并附文档链接。
- **Base URL 端点自动补全**：`endpointURL()` 将 `https://api.deepseek.com` 归一化为 `/chat/completions`。

### 涉及文件
- `index.html`

---

## [v1.2] - 2026-08-09

### 新增
- **可配置大模型 API 接入**：⚙ API 弹窗（Base URL / Key / 模型 / 用大模型生成对话），配置后对话与 AI 总评走用户自己的大模型；未配置时回退内置规则引擎（后于 v2.0 移除）。
- Key 仅存本机浏览器 `localStorage`。

### 涉及文件
- `index.html`

---

## [v1.1] - 2026-08-09

### 修改
- 与参考网页统一「纸感 / 墨绿 / 荧光黄」brutalist 风格；主界面复刻参考文件结构（Hero / 训练对象卡片 / 训练方式 / 训练场），答辩分析模块同风格保留。

### 涉及文件
- `高压沟通教练.html`

---

## [v1.0] - 2026-08-08

### 新增
- 首个单文件交互网页 `高压沟通教练.html`：选张总 / 严老师进行高压对话训练，结束后自动生成可视化答辩复盘（雷达、评分、失分点、高压话翻译表、时间线、示范回答、下一轮重点、导出报告）。

### 涉及文件
- `高压沟通教练.html`
