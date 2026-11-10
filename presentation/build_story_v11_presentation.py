"""Add overseas-market conversation and evidence-based English coaching to the deck."""
from pathlib import Path
import json
from PIL import Image
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
ROOT=Path(__file__).resolve().parent;A=ROOT/'assets-v11';prs=Presentation(ROOT/'AI-workplace-coach-story-v10.pptx');rows=json.loads((ROOT/'story-v10-content.json').read_text())
def text(sl,x,y,w,h,s,size=18,color='4C4948',bold=False):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 r=tf.paragraphs[0].add_run();r.text=s;r.font.name='Noto Sans CJK SC';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
 ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)
def picture(sl,name,x,y,w=None,h=None):
 kw={'width':Inches(w)} if w else {'height':Inches(h)}
 return sl.shapes.add_picture(str(A/name),Inches(x),Inches(y),**kw)
def slide(title):
 sl=prs.slides.add_slide(prs.slide_layouts[2])
 for sh in list(sl.shapes):
  if sh!=sl.shapes.title:sl.shapes._spTree.remove(sh._element)
 sl.shapes.title.text='第二部分  应用成效'
 for r in sl.shapes.title.text_frame.paragraphs[0].runs:r.font.name='Noto Sans CJK SC';r.font.size=Pt(24);r.font.bold=True;r.font.color.rgb=RGBColor.from_string('4C4948')
 text(sl,.55,1.02,9,.5,title,25,bold=True);picture(sl,'nav-practice.png',.65,1.67,w=8.7)
 text(sl,.65,6.98,8.7,.18,'真实界面实拍｜虚构海外案例；对话、评分与语言建议为本机替身数据，非真实模型效果实测',8,'727171')
 return sl
newrows=[];newids=[]
sl=slide('面向海外客户，把技术说明与英语表达一起练。')
im=Image.open(A/'overseas-example.png');cut=json.loads((A/'example-layout.json').read_text())['splitY']
for name,box,x in [('example-top.png',(0,0,im.width,cut),.65),('example-bottom.png',(0,cut,im.width,im.height),5.1)]:im.crop(box).save(A/name);picture(sl,name,x,2.32,w=4.2)
text(sl,.7,6.30,8.6,.47,'交期协调 · 验收澄清 · 进度更新：三轮英文示例，对照较弱与改进表达。',15,'C70019',True)
newrows.append(dict(title='面向海外客户，把技术说明与英语表达一起练。',body='用海外客户交付协调示例，把业务沟通与语言表达连接起来。',seconds=40,point='沟通训练标签下选择“海外客户·英语”；指三轮对照与“使用此示例目标与背景”。',speech='面向海外市场，事情讲清楚和英语表达得体，需要一起练。这里新增了一个完整的海外客户交付协调示例：客户要求确认交期，我们既要说明验证边界，也要把英语请求说得准确自然。三轮示例提供较弱表达与改进表达，目标和背景可以直接载入，正式对话仍由配置的模型生成。',transition='接下来，看它如何在连续英文对话里提出追问。',appendix=False))
newids.append(prs.slides._sldIdLst[-1])
sl=slide('英文连续追问，中文解释客户真正关心什么。')
picture(sl,'overseas-dialogue.png',.7,2.32,w=4.25)
text(sl,5.25,2.37,4.05,.35,'客户要确认的不只是一个日期。',18,'C70019',True)
text(sl,5.25,2.98,4.0,1.0,'Can you guarantee delivery by Friday?\n客户希望据此安排安装团队。',16)
picture(sl,'overseas-score.png',5.15,4.13,w=4.15)
text(sl,5.25,5.25,4.05,1.25,'练习回应：说明验证现状，保留承诺边界，再明确下一次更新。\n英文对话 / 中文解读与复盘',17)
newrows.append(dict(title='英文连续追问，中文解释客户真正关心什么。',body='以海外客户的真实工作诉求组织追问，训练英文澄清与承诺边界。',seconds=40,point='左边指客户交期、未完成验证、后续更新三个问题；右边指出业务总分独立保留。',speech='客户问周五能否交付，并不只是问英语句子，而是在安排安装资源。因此训练会围绕交期、未验证条件和后续更新连续推进。对话使用英文，三层解读和复盘用中文，帮助用户理解问题背后的工作诉求。原有六维评分保留，语言是否流利不能替代证据和交付边界。',transition='在业务复盘之外，再单独看英语表达怎么改。',appendix=False))
newids.append(prs.slides._sldIdLst[-1])
sl=slide('从用户原句出发，让英语表达有具体的改法。')
picture(sl,'language-review.png',.75,2.32,h=4.4)
text(sl,5.15,2.35,4.1,.4,'原句 → 英文改写 → 中文解释',18,'C70019',True)
text(sl,5.15,3.00,4.05,1.05,'语法准确\nnot finish → is not yet complete',17)
text(sl,5.15,4.13,4.05,1.05,'商务得体\nYou must… → Could you please…?',17)
text(sl,5.15,5.25,4.05,1.35,'技术术语与下一轮练习\nacceptance criteria：验收标准\n再练一次具体、得体的澄清请求。',16)
newrows.append(dict(title='从用户原句出发，让英语表达有具体的改法。',body='逐句对照、中文原因、技术术语与英语练习共同支持语言提升。',seconds=45,point='左图指原句与改写、中文解释、术语和练习；右边放大两个真实对应的语言点。',speech='新增的英语表达提升不是一段笼统评价，而是逐条引用用户实际说过的英文，给出保留原意的改写和中文原因。比如not finish的语法问题，以及You must在客户请求中的生硬语气。相关技术术语和下一次练习也一起保留。语言建议与业务六维总分分开，文本训练不评价发音、听力或英语等级。这些画面是虚构演示，真实模型效果还需要实际服务验证。',transition='无论国内协作还是海外客户，训练中的观察都可以继续积累到沟通画像。',appendix=False))
newids.append(prs.slides._sldIdLst[-1])
# Insert after the original domestic practice flow, before longitudinal portrait.
for i,sid in enumerate(newids):prs.slides._sldIdLst.remove(sid);prs.slides._sldIdLst.insert(12+i,sid)
rows[11]['transition']='同样的训练方式，也可以用于面向海外市场的英语沟通。'
rows[12:12]=newrows
# Keep background concise while acknowledging the newly added overseas-market capability.
sl=prs.slides[1]
for sh in sl.shapes:
 if sh.has_text_frame and '汇报进度、评审方案、协调客户' in sh.text:
  for r in sh.text_frame.paragraphs[0].runs:r.text=r.text.replace('汇报进度、评审方案、协调客户','国内协作、技术评审、海外客户沟通')
for i,(sl,row) in enumerate(zip(prs.slides,rows),1):
 row['page']=i
 for sh in list(sl.shapes):
  if sh.has_text_frame and sh.text.strip().isdigit() and sh.top>Inches(7):sl.shapes._spTree.remove(sh._element)
 if i not in [1,len(rows)]:text(sl,.54,7.1,.45,.23,str(i).zfill(2),9,'727171')
 sl.notes_slide.notes_text_frame.text=f'【建议停留】{row["seconds"]}秒\n【本页一句话】{row["body"]}\n【看图指向】{row["point"]}\n【讲述稿】\n{row["speech"]}\n【转场】\n{row["transition"]}'
prs.core_properties.title='AI职场沟通训练师｜第十一版 · 海外客户与英语表达提升'
prs.save(ROOT/'AI-workplace-coach-story-v11.pptx');(ROOT/'story-v11-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
md=['# 第十一版讲述稿','','32页；第13–15页新增海外客户英语沟通、连续追问与英语专项提升；保留精简背景、API入口、首页及复盘全貌。','']
for r in rows:md.extend([f'## {r["page"]:02d}｜{r["title"]}','','讲述：'+r['speech'],'','转场：'+r['transition'],''])
(ROOT/'项目展示内容与讲述稿-第十一版.md').write_text('\n'.join(md))
print('v11 built:32 slides; overseas 13–15')
