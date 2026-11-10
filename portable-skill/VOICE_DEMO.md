# 海外客户语音演示（四句）

这是虚构练习。先在文字会话上传SKILL.md与report-template.md，并发送：

> 按附件Skill进行海外客户语音训练。你是客户项目经理，我是供应商工程师。已知事实仅为常温测试完成、高温验证未完成。按下面两轮客户提问推进，每次等我回答；不要抢答我的台词。对话用英文。听到“结束并复盘”后，按Skill生成中文报告，包含六维与每轮分数、逐字原话依据、英文改写和中文解释。不要预设分数。若语音模式无法访问附件或转写，请先告诉我。

开启语音后：

1. **GPT（海外客户）**：Can you guarantee delivery by Friday? We need to arrange installation.
2. **你**：Room-temperature testing is complete, but high-temperature validation is still pending. I cannot confirm Friday delivery yet. Could you confirm the operating conditions and acceptance criteria?
3. **GPT（海外客户）**：We will send those requirements today. Can you give us an update by four p.m. UTC tomorrow?
4. **你**：Yes. I will send you the validation status, delivery options and remaining risks by four p.m. UTC tomorrow.

最后说“结束并复盘”。这句是控制指令，不算训练回应。

录制建议：先录附件加载与规则确认，再录四句通话，最后切回文字展示报告。实际提问或转写有变化时，报告必须依据实际记录，不套用脚本、不预置成绩。只有两条用户回应，画像判断应标注初步且有限。

可追加：请把本次报告整理为可下载的Markdown。若宿主无法生成文件，则在聊天完整展示报告。
