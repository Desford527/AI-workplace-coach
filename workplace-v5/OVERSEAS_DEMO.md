# 海外客户英语演示与验收（v5.1.0）

## 怎么演示

1. 打开 `workplace-v5/start.bat`（或 `python server.py 8000`）。
2. 选择「海外客户 · 英语」→「英文交付协调会议」。
3. 展开示例查看三轮弱/强对照，点击「使用此示例目标与背景」。
4. 点击「进入连续对话」，用下面的回应练习；模型实际提问可能不同，请结合问题调整。
5. 结束并复盘，查看六维业务评分与单独的「英语表达提升」，可导出HTML。

## 虚构示例脚本

目标：用准确、自然、得体的英文说明验证边界，澄清验收条件，并约定下一次更新。

背景：虚构练习：设备常温测试已完成，高温验证未闭环。海外客户需要安排安装。不得承诺尚未确认的交期；请先确认工况与验收标准。

### 第1轮

客户：Can you guarantee delivery by Friday? Our installation team needs a firm date.

较弱回应：Yes, no problem. We will try our best.

改进回应：I understand that your installation team needs a firm date. Room-temperature testing is complete, but high-temperature validation is still pending. I cannot confirm Friday delivery yet. Could we agree on an update time while we review the remaining work?

语言与业务说明：try our best 无法替代交付承诺；先回应客户影响，再说明验证边界。

### 第2轮

客户：What exactly is still open, and what do you need from us?

较弱回应：The test is not finish. You must give us the data quickly.

改进回应：High-temperature validation is not yet complete. Could you please confirm the operating temperature range and acceptance criteria? This will help us align the remaining tests with your application.

语言与业务说明：not finish 改为 is not yet complete；用 Could you please 说明具体请求，避免生硬命令。

### 第3轮

客户：How will you keep us informed if the schedule changes?

较弱回应：We will feedback you later. Please wait.

改进回应：I will send you an update by [agreed time], including the validation status, delivery options and any remaining risks. Could you confirm who should receive the update?

语言与业务说明：feedback 通常用作名词；用 send you an update，并明确时间、内容和接收人。

## 验收与未实测

- 69项后端测试通过，包括英文复盘持久化、真实用户引文校验、拒绝伪造/错误角色引用、缺失语言补充的兼容处理。
- 原有桌面/手机、API多配置、对象CRUD、训练/复盘、画像、HTML/PDF导出浏览器回归通过。
- 自由输入、经验库与四主题手机回归通过。
- 新增海外流程：示例载入、3条英文回应、2条语言改写、中文解释、术语、390px手机显示、HTML导出通过，浏览器错误0。
- 截图为独立临时目录的虚构模型替身数据。真实服务商连接、真实模型语言反馈质量、Windows CMD和PowerPoint未在本次实机验证。
- 英语是本次落实的外语；尚未实现其他语种、语音输入、发音与听力评分。
- 未更改原有默认API文件、用户密钥配置和训练数据库。旧复盘可继续阅读，新增报告才会请求逐句语言补充。
- 不覆盖旧目录：解压到新目录先运行。已有配置及历史请使用项目迁移工具/原有迁移流程导入新副本，勿用演示数据替换。
