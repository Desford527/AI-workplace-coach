"""Replace introduction overview with two continuous halves of the real homepage."""
from pathlib import Path
import json
from PIL import Image
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
ROOT=Path(__file__).resolve().parent
prs=Presentation(ROOT/'AI-workplace-coach-story-v6.pptx')
rows=json.loads((ROOT/'story-v6-content.json').read_text())
sl=prs.slides[4]
for sh in list(sl.shapes):
 if sh!=sl.shapes.title:sl.shapes._spTree.remove(sh._element)
def text(x,y,w,h,s,size=18,color='4C4948',bold=False):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True
 tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 r=tf.paragraphs[0].add_run();r.text=s;r.font.name='Noto Sans CJK SC';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
 ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)
sl.shapes.title.text='第一部分  项目简介'
for r in sl.shapes.title.text_frame.paragraphs[0].runs:
 r.font.name='Noto Sans CJK SC';r.font.size=Pt(24);r.font.bold=True;r.font.color.rgb=RGBColor.from_string('4C4948')
text(.55,1.02,9,.48,'先看网页全貌，再走进一次真实的沟通练习。',25,bold=True)
text(.70,1.65,4.2,.23,'01  首页上半页 · 介绍、导航与训练入口',12,'C70019',True)
text(5.15,1.65,4.3,.23,'02  接续下半页 · 会议纪要与「直接说」',12,'C70019',True)
im=Image.open(ROOT/'assets-v8/home-full.png');cut=im.height//2
for name,box,x in [('home-top.png',(0,0,im.width,cut),.70),('home-bottom.png',(0,cut,im.width,im.height),5.15)]:
 part=im.crop(box);path=ROOT/'assets-v8'/name;part.save(path)
 h=5.04;w=h*part.width/part.height
 sl.shapes.add_picture(str(path),Inches(x+(4.15-w)/2),Inches(1.99),height=Inches(h))
text(.54,7.1,.45,.23,'05',9,'727171')
text(1.20,7.13,8.3,.20,'真实首页连续截图 · 左侧从页首开始，右侧接续至页尾 · 本机空白演示环境',9,'727171')
rows[4].update(title='先看网页全貌，再走进一次真实的沟通练习。',body='一张首页长截图分为左右两段，先建立产品全貌，再进入功能细节。',point='按左上→左下→右上→右下浏览；先指顶部与五个标签，再指纪要和直接说。',speech='这就是项目的完整首页。左边从页首开始，可以看到产品定位、五个标签页和训练入口；右边接着往下，是导入会议纪要、项目资料和想改什么直接说。页面把练习和资料积累放在同一个空间里。先记住这张全貌，接下来我们沿着一次向朱总汇报交付的任务，逐步看看它怎么用。',transition='正式练习前，先说明模型从哪里接入。',seconds=35)
for slide,row in zip(prs.slides,rows):
 slide.notes_slide.notes_text_frame.text=f'【建议停留】{row["seconds"]}秒\n【本页一句话】{row["body"]}\n【看图指向】{row["point"]}\n【讲述稿】\n{row["speech"]}\n【转场】\n{row["transition"]}'
prs.core_properties.title='AI职场沟通训练师｜第八版 · 首页全貌'
prs.core_properties.subject='背景介绍后以左右连续截图展示完整首页，无视频'
prs.save(ROOT/'AI-workplace-coach-story-v8.pptx')
(ROOT/'story-v8-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
md=['# 第八版讲述稿','','共30页；取消视频，背景、问题和方案之后，第5页展示真实首页全貌。API第6页，直接说第22–25页。截图为本机隔离演示环境，未调用真实模型。','']
for r in rows:md.extend([f'## {r["page"]:02d}｜{r["title"]}','','讲述：'+r['speech'],'','转场：'+r['transition'],''])
(ROOT/'项目展示内容与讲述稿-第八版.md').write_text('\n'.join(md))
print('v8: 30 slides; homepage overview page 5; no video')
