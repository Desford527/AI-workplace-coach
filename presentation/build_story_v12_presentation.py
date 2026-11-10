"""Expression optimization: original user-chosen phrase versus audience-aware request."""
from pathlib import Path
import json
from PIL import Image
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
ROOT=Path(__file__).resolve().parent;A=ROOT/'assets-v12';prs=Presentation(ROOT/'AI-workplace-coach-story-v11.pptx');rows=json.loads((ROOT/'story-v11-content.json').read_text())
def text(sl,x,y,w,h,s,size=18,color='4C4948',bold=False):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 r=tf.paragraphs[0].add_run();r.text=s;r.font.name='Noto Sans CJK SC';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
 ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)
# Refresh full homepage to show the new expression tab; no change to previous versions.
home=prs.slides[2];pictures=[s for s in home.shapes if s.shape_type==13];im=Image.open(A/'home-full.png');cut=im.height//2
for old,name,box in zip(pictures,['home-top.png','home-bottom.png'],[(0,0,im.width,cut),(0,cut,im.width,im.height)]):
 im.crop(box).save(A/name);home.shapes.add_picture(str(A/name),old.left,old.top,width=old.width,height=old.height);home.shapes._spTree.remove(old._element)
sl=prs.slides.add_slide(prs.slide_layouts[2])
for sh in list(sl.shapes):
 if sh!=sl.shapes.title:sl.shapes._spTree.remove(sh._element)
sl.shapes.title.text='第二部分  应用成效'
for r in sl.shapes.title.text_frame.paragraphs[0].runs:r.font.name='Noto Sans CJK SC';r.font.size=Pt(24);r.font.bold=True;r.font.color.rgb=RGBColor.from_string('4C4948')
text(sl,.55,1.02,9,.5,'表达优化：把情绪化抱怨，转成合理的诉求。',25,bold=True)
sl.shapes.add_picture(str(A/'nav-expression.png'),Inches(.65),Inches(1.67),width=Inches(8.7))
text(sl,.7,2.29,4.25,.65,'原话输入（情绪化示例）\n“我觉得朱彦霖脑子有问题”',18,'C70019',True)
sl.shapes.add_picture(str(A/'expression-input.png'),Inches(.7),Inches(3.13),width=Inches(4.15))
text(sl,.75,5.42,4.05,1.3,'选择朱总等现有对象或通用对象；\n补充背景与期望，生成完整和简短表达。\n只生成草稿，由用户确认后使用。',16)
sl.shapes.add_picture(str(A/'expression-result.png'),Inches(5.15),Inches(2.32),width=Inches(4.15))
text(sl,.65,6.98,8.7,.18,'虚构情绪化示例，不作为对现实人物的评价｜真实界面；改写为本机模型替身数据，未验证真实模型效果',8,'727171')
sid=prs.slides._sldIdLst[-1];prs.slides._sldIdLst.remove(sid);prs.slides._sldIdLst.insert(15,sid)
rows[14]['transition']='除了练外语，临时想说的一句气话，也可以先整理一下。'
rows.insert(15,dict(title='表达优化：把情绪化抱怨，转成合理的诉求。',body='选择现有或通用对象，将原话整理为具体问题、工作诉求与可直接使用的表达。',seconds=40,point='左侧先读原话，再指沟通对象和期望；右侧展示完整表达、简短版和待补充项。',speech='有时我们想说的第一句话，是一句气话。比如左边这句“我觉得朱彦霖脑子有问题”，这里仅作为情绪化输入示例。选择说给朱总听，再补充希望协调分工的目标，系统会把人身评价转成协作困扰和明确请求。右边同时给完整表达、简短版和待补充的信息，不会编造同事做过什么，也不会自动发送。对象既可以从现有画像选择，也可以使用通用对象，还支持英文表达。',transition='整理好的表达可以自行修改使用；训练中的原话与复盘，则继续积累到沟通画像。',appendix=False))
for i,(slide,row) in enumerate(zip(prs.slides,rows),1):
 row['page']=i
 for sh in list(slide.shapes):
  if sh.has_text_frame and sh.text.strip().isdigit() and sh.top>Inches(7):slide.shapes._spTree.remove(sh._element)
 if i not in [1,len(rows)]:text(slide,.54,7.1,.45,.23,str(i).zfill(2),9,'727171')
 slide.notes_slide.notes_text_frame.text=f'【建议停留】{row["seconds"]}秒\n【本页一句话】{row["body"]}\n【看图指向】{row["point"]}\n【讲述稿】\n{row["speech"]}\n【转场】\n{row["transition"]}'
prs.core_properties.title='AI职场沟通训练师｜第十二版 · 表达优化'
prs.save(ROOT/'AI-workplace-coach-story-v12.pptx');(ROOT/'story-v12-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
md=['# 第十二版讲述稿','','33页，第16页新增表达优化；第3页首页更新为含表达优化入口的真实截图。','']
for r in rows:md.extend([f'## {r["page"]:02d}｜{r["title"]}','','讲述：'+r['speech'],'','转场：'+r['transition'],''])
(ROOT/'项目展示内容与讲述稿-第十二版.md').write_text('\n'.join(md));print('v12:33 slides, expression page16')
