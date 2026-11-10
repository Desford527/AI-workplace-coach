"""Add a real full-report overview ahead of score and review detail slides."""
from pathlib import Path
import json
from PIL import Image
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
ROOT=Path(__file__).resolve().parent;prs=Presentation(ROOT/'AI-workplace-coach-story-v9.pptx');rows=json.loads((ROOT/'story-v9-content.json').read_text())
def text(sl,x,y,w,h,s,size=18,color='4C4948',bold=False):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 r=tf.paragraphs[0].add_run();r.text=s;r.font.name='Noto Sans CJK SC';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
 ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)
sl=prs.slides.add_slide(prs.slide_layouts[2])
for sh in list(sl.shapes):
 if sh!=sl.shapes.title:sl.shapes._spTree.remove(sh._element)
sl.shapes.title.text='第二部分  应用成效'
for r in sl.shapes.title.text_frame.paragraphs[0].runs:r.font.name='Noto Sans CJK SC';r.font.size=Pt(24);r.font.bold=True;r.font.color.rgb=RGBColor.from_string('4C4948')
text(sl,.55,1.02,9,.48,'练完之后，得到一份完整的沟通复盘。',25,bold=True)
text(sl,.70,1.65,4.2,.23,'01  总分、六维表现与关键问题',12,'C70019',True)
text(sl,5.15,1.65,4.3,.23,'02  逐轮评分、原话分析与下一轮建议',12,'C70019',True)
im=Image.open(ROOT/'assets-v10/review-full.png');cut=json.loads((ROOT/'assets-v10/capture.json').read_text())['splitY']
for name,box,x in [('review-top.png',(0,0,im.width,cut),.70),('review-bottom.png',(0,cut,im.width,im.height),5.15)]:
 part=im.crop(box);path=ROOT/'assets-v10'/name;part.save(path);h=5.04;w=h*part.width/part.height
 sl.shapes.add_picture(str(path),Inches(x+(4.15-w)/2),Inches(1.99),height=Inches(h))
text(sl,1.20,7.13,8.3,.20,'真实界面连续截图 · 本机虚构演示数据 · 评分与分析非真实模型或业务效果实测',9,'727171')
sid=prs.slides._sldIdLst[-1];prs.slides._sldIdLst.remove(sid);prs.slides._sldIdLst.insert(7,sid)
rows[6]['transition']='回应结束之后，先整体看一眼这份复盘报告。'
rows.insert(7,dict(page=8,title='练完之后，得到一份完整的沟通复盘。',body='先看报告全貌，再细看总分、六维表现和逐轮改进。',seconds=35,point='左侧先指68分和雷达图；再沿右侧指出每轮分数、原话解读与下一轮计划。',speech='训练结束后，用户拿到的是这样一份完整复盘。左侧先给总分、六个维度和关键问题，右侧接着回到每轮原话，给出逐轮分数、改进示范和下一轮建议。它把结果、依据和改进方向放在同一份报告里。这一页先看结构，后面我们把分数和改进示范分别放大看。这里展示的是本机虚构案例，不是真实业务效果实测。',transition='先从这份报告最醒目的总分说起。',appendix=False))
for i,(slide,row) in enumerate(zip(prs.slides,rows),1):
 row['page']=i
 for sh in list(slide.shapes):
  if sh.has_text_frame and sh.text.strip().isdigit() and sh.top>Inches(7):slide.shapes._spTree.remove(sh._element)
 if i not in [1,len(rows)]:text(slide,.54,7.1,.45,.23,str(i).zfill(2),9,'727171')
 slide.notes_slide.notes_text_frame.text=f'【建议停留】{row["seconds"]}秒\n【本页一句话】{row["body"]}\n【看图指向】{row["point"]}\n【讲述稿】\n{row["speech"]}\n【转场】\n{row["transition"]}'
prs.core_properties.title='AI职场沟通训练师｜第十版 · 完整复盘总览'
prs.save(ROOT/'AI-workplace-coach-story-v10.pptx');(ROOT/'story-v10-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
md=['# 第十版讲述稿','','共29页；保留精简背景、首页全貌、API按钮定位。第8页新增完整复盘总览，后接评分与分析细节。','']
for r in rows:md.extend([f'## {r["page"]:02d}｜{r["title"]}','','讲述：'+r['speech'],'','转场：'+r['transition'],''])
(ROOT/'项目展示内容与讲述稿-第十版.md').write_text('\n'.join(md))
print('v10:29 pages, full review overview page8')
