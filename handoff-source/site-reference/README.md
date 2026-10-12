# AI职场沟通训练师 v1.3

## 产品能力

- 双方画像：AI综合真实训练形成长期个人画像，展示行为特征、优势、原话证据、改进练法与历史变化，无自评表；对象职责、关系、目标、标准、风格、原话、事实、推断与模拟边界。
- 四类八场景，英文训练中文复盘。自建对象可新增、编辑、删除，内置虚拟角色可另存修改。
- 每轮创建画像快照，后续画像修改不会污染历史训练。
- 在线画像与训练记录保存在 D1，按平台认证用户隔离；版本校验防止覆盖。
- Sites MCP 插件供 ChatGPT 读取画像、建立训练、保存真实开场、逐轮回应和证据化复盘。
- 在线网页直接调用本站后端，后端通过OpenAI Responses API生成连续追问、复盘及长期画像；凭据仅保存在Sites后端密钥中。原MCP资料读写能力保留。
- 复盘包含五维分数与理由/原话证据、可能意图、逐轮分析、示范回答和下一轮重点。证据不足可待评。
- 单文件版用于网址无法访问时：画像和记录为本次文件会话状态，需导出JSON备份；复制训练资料在ChatGPT开展训练，实际原话手工录入、复盘JSON导入。

## 插件工具

read_workspace、update_communication_profile、save_object_profile、delete_object_profile、create_training_session、read_training_session、append_training_message、save_training_review、archive_training_session。

插件安装连接后方能在对话中调用。不能把“已提供MCP接口”当作“用户已连接”。

## 技术结构

web/ 前端源；shared/ 场景与内置画像；worker/index.js ESM Worker；db/schema.ts Drizzle模型；drizzle/ 生成迁移；scripts/build-coach.mjs 打包。

生成命令：npm run db:generate（仅模式变更时）；npm run build。生产通过 Sites 发布，原站点身份与私有访问保持不变。

## 验证

语法、ESM入口、SQLite迁移与乐观更新SQL、模拟D1接口、MCP发现与匿名拒绝、跨用户隔离、跨站写入保护、画像快照、消息交替、真实证据复盘校验、模拟DOM文件版完整流程通过。真实浏览器视觉和用户连接后的远程插件实测待完成。

## 长期画像

首次训练无需画像。每次ChatGPT保存真实复盘后，读取已有画像及引用的训练，调用update_communication_profile更新综合观察。服务端校验所有来源的所有权、复盘状态、版本及每项原话证据；保留旧来源，最多12次画像历史。单轮标记初步观察，跨至少3轮有证据的观察标为多轮观察。旧自评数据保留，但不作为AI观察展示或训练前置。网页只负责同步展示，不自行执行模型调用。

## 网页直接训练

配置Sites后端secret OPENAI_API_KEY，可选env OPENAI_MODEL（默认gpt-4.1-mini）。请通过OpenAI Developers安全配置流程设置；不将密钥写入浏览器、源码或manifest。模型API独立计费。未配置时read_workspace返回ai.enabled=false，训练按钮不可用，无伪造回复。

网页依次执行create_training_session与ai_reply生成开场；真实回应保存后自动ai_reply；ai_review先保存验证后的评分复盘，再调用模型综合历史并校验更新长期画像。画像失败时保留已完成复盘，可单独ai_portrait重试。所有AI请求需要平台用户身份、训练版本与请求ID，每用户有带过期时间的CAS处理锁，成功重复请求复用记录，避免重复发送。每次调用使用store:false及严格JSON schema，生成结果仍做原话证据校验。超时、限额和认证失败显示明确状态，原对话保留。

已通过模拟模型与D1的完整前后端流程、并发/重复请求、上游失败、跨用户与证据验证测试。真实模型联调等待凭据。

## v1.4 基础演练

未配置模型时仍可直接开始：aiConfiguration返回enabled=true, mode=basic，创建训练时冻结engine=basic，按八场景原开场及表达线索生成追问，保留真实消息，生成逐轮规则分析、带占位符的场景示范和练习方向。基础模式所有能力分为null，明确标注不是AI语义或能力测量。规则画像引用真实回应，标为待验证，不覆盖既有AI画像。配置模型后新训练使用AI，既有基础轮次仍保持基础方式。

验证：node tests/basic.mjs，实际SQLite内存数据库、8个场景、英文、全程无模型请求、画像证据/用户隔离及前端开始-回应-复盘操作流程。

## v1.5 视觉与工程场景

借鉴用户提供HTML的纸色、深绿、亮黄、高对比标题与硬边阴影视觉，保留职场定位与工作台功能。新增由实际场景数据驱动的开场预览，将开始按钮移到场景标题旁。基础技术演练增加器件耐压、控制稳定性和效率范围主题追问，仍明确标注规则性质。
