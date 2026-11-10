"""Portable Skill evidence and GitHub closing page; voice demo is user-recorded later."""
from pathlib import Path
import json
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
ROOT=Path(__file__).resolve().parent;prs=Presentation(ROOT/'AI-workplace-coach-story-v13.pptx');rows=json.loads((ROOT/'story-v13-content.json').read_text())
def text(sl,x,y,w,h,s,size=18,color='4C4948',bold=False,url=None):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 for i,line in enumerate(s.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();r=p.add_run();r.text=line;r.font.name='Noto Sans CJK SC';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
  ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)
  if url:r.hyperlink.address=url
 return sh
sl=prs.slides.add_slide(prs.slide_layouts[2])
for sh in list(sl.shapes):
 if sh!=sl.shapes.title:sl.shapes._spTree.remove(sh._element)
sl.shapes.title.text='第三部分  复用与推广'
for r in sl.shapes.title.text_frame.paragraphs[0].runs:r.font.name='Noto Sans CJK SC';r.font.size=Pt(24);r.font.bold=True;r.font.color.rgb=RGBColor.from_string('4C4948')
text(sl,.55,1.02,9,.56,'一个 Skill，把沟通训练带到更多 AI 应用。',25,bold=True)
text(sl,.7,1.9,4.3,.4,'已形成可导入的 Skill 文件',19,'C70019',True)
text(sl,.75,2.65,4.05,1.15,'workplace-communication-coach/\n  SKILL.md\n  references/report-template.md',16,bold=True)
text(sl,.75,4.05,4.05,1.5,'对象模拟与连续追问\n英语训练与逐句语言改进\n六维评分、逐轮复盘\n表达优化、纪要与画像建议',17)
text(sl,5.1,1.9,4.25,.4,'从文字训练，延伸到口头交流',19,'C70019',True)
text(sl,5.15,2.62,4.05,2.25,'01  导入 Skill 或上传规则文件\n\n02  在支持的应用中开启语音\n\n03  用实际转写生成复盘报告',18,bold=True)
text(sl,5.15,5.15,4.05,.85,'演示：与 GPT 模拟海外客户通话，结束后展示同结构报告。',17)
text(sl,.75,6.32,8.5,.52,'兼容性取决于宿主：需支持 Skill 或附件指令；语音与跨会话保存由宿主提供。',12,'727171')
text(sl,.75,6.88,8.5,.18,'已附可迁移文件；GPT语音演示视频待录制，尚未声称完成平台兼容实测。',9,'727171')
sid=prs.slides._sldIdLst[-1];prs.slides._sldIdLst.remove(sid);prs.slides._sldIdLst.insert(32,sid)
rows[31]['transition']='除了网页应用，这套训练方法也整理成了可迁移的Skill。'
rows.insert(32,dict(title='一个 Skill，把沟通训练带到更多 AI 应用。',body='核心训练方法已封装为Skill；支持附件指令或原生Skill的AI可加载，语音取决于宿主。',point='左边是真实交付文件和可复用能力；右边说明加载、语音训练、按原话生成报告三步。',seconds=40,speech='本项目还形成了一份可迁移的Skill，把对象模拟、英文训练、六维复盘和表达优化整理成明确规则。支持Skill的Agent可以导入，支持附件指令的AI也可以加载规则。在能够共享这些规则和转写的语音应用中，就能口头扮演海外客户，结束后按同样结构复盘。这里复用的是训练方法；网页记录管理和长期数据库仍由应用承担。接下来可以播放实际录制的通话与报告演示。',transition='项目与Skill文件，都可以从GitHub获取。',appendix=False))
# Preserve original corporate closing design, replace its text with the requested GitHub announcement.
last=prs.slides[-1]
for sh in list(last.shapes):
 if sh.has_text_frame:last.shapes._spTree.remove(sh._element)
text(last,.94,3.95,8.15,.65,'本项目已公开发布',30,bold=True)
text(last,.94,4.78,8.15,.44,'在 GitHub 获取项目与 Skill',21,'C70019',True)
url='https://github.com/Desford527/AI-workplace-coach'
text(last,.94,5.48,8.15,.75,'github.com/Desford527/\nAI-workplace-coach',20,bold=True,url=url)
text(last,.94,6.55,8.15,.36,'项目源码 · 本地启动 · 演示资料 · 可迁移 Skill',15)
rows[-1].update(title='本项目已公开发布，在GitHub获取项目与Skill。',body='提供GitHub项目入口，公开权限由用户切换；匿名可访问性待切换后复核。',point='展示仓库地址，可点击进入。',speech='本项目及可迁移的Skill可以在GitHub获取。欢迎下载、运行，并结合自己的工作对象和沟通场景继续完善。',transition='谢谢大家。',seconds=20)
for i,(slide,row) in enumerate(zip(prs.slides,rows),1):
 row['page']=i
 for sh in list(slide.shapes):
  if sh.has_text_frame and sh.text.strip().isdigit() and sh.top>Inches(7):slide.shapes._spTree.remove(sh._element)
 if i not in [1,len(rows)]:text(slide,.54,7.1,.45,.23,str(i).zfill(2),9,'727171')
 slide.notes_slide.notes_text_frame.text=f'【建议停留】{row["seconds"]}秒\n【本页一句话】{row["body"]}\n【看图指向】{row["point"]}\n【讲述稿】\n{row["speech"]}\n【转场】\n{row["transition"]}'
prs.core_properties.title='AI职场沟通训练师｜第十四版 · Skill复用与GitHub发布'
prs.save(ROOT/'AI-workplace-coach-story-v14.pptx');(ROOT/'story-v14-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
md=['# 第十四版讲述稿','','34页：第33页Skill与口头交流路径，第34页GitHub获取。公开权限由用户切换，交付时匿名访问尚待验证。','']
for r in rows:md.extend([f'## {r["page"]:02d}｜{r["title"]}','','讲述：'+r['speech'],'','转场：'+r['transition'],''])
(ROOT/'项目展示内容与讲述稿-第十四版.md').write_text('\n'.join(md));print('v14 built:34 pages')
