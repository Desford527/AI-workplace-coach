"""Make slide02 a concise introduction plus a replaceable video area."""
from pathlib import Path
import json
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
from pptx.enum.shapes import MSO_SHAPE
ROOT=Path(__file__).resolve().parent;prs=Presentation(ROOT/'AI-workplace-coach-story-v16.pptx');rows=json.loads((ROOT/'story-v16-content.json').read_text())
def text(sl,x,y,w,h,s,size=18,color='4C4948',bold=False):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 for i,line in enumerate(s.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();r=p.add_run();r.text=line;r.font.name='Noto Sans CJK SC';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
  ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)
sl=prs.slides[1]
for sh in list(sl.shapes):
 if sh!=sl.shapes.title:sl.shapes._spTree.remove(sh._element)
text(sl,.55,1.02,9,.56,'重要沟通，先练一遍。',28,bold=True)
text(sl,.65,1.77,8.7,.36,'面对关键追问，把判断说清楚，把诉求讲具体。',18)
frame=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(.8),Inches(2.35),Inches(8.4),Inches(4.725));frame.fill.solid();frame.fill.fore_color.rgb=RGBColor.from_string('FAF7F5');frame.line.color.rgb=RGBColor.from_string('EADBD7');frame.name='INTRO_VIDEO_REPLACE_HERE'
play=sl.shapes.add_shape(MSO_SHAPE.OVAL,Inches(4.52),Inches(3.75),Inches(.96),Inches(.96));play.fill.solid();play.fill.fore_color.rgb=RGBColor.from_string('C70019');play.line.fill.background();play.name='INTRO_VIDEO_PLAY_BUTTON'
tri=sl.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE,Inches(4.85),Inches(4.04),Inches(.32),Inches(.36));tri.rotation=90;tri.fill.solid();tri.fill.fore_color.rgb=RGBColor.from_string('FFFFFF');tri.line.fill.background()
text(sl,2.1,5.02,5.8,.44,'AI职场沟通训练师 · 项目简介',21,bold=True)
text(sl,.54,7.1,.45,.23,'02',9,'727171')
rows[1].update(title='重要沟通，先练一遍。',body='一句话说明沟通难点，随后播放项目简介视频。',point='本页预留大幅简介视频位置，优化版视频由用户插入或关联。',speech='准备了很多材料，面对关键追问，仍然可能说不清楚。这个项目帮助我们把重要沟通提前练一遍。先用一段短片，看它如何连接练习、复盘和改进。',transition='视频里看到了整体思路，接下来看看实际网页怎样承接这些能力。',seconds=55)
sl.notes_slide.notes_text_frame.text=f'【讲述】\n{rows[1]["speech"]}\n【转场】\n{rows[1]["transition"]}\n本页仅预留视频位置，尚未嵌入MP4。'
# Remove repetitive editorial footnotes; retain their content in speaker notes.
removed=[]
for page,slide in enumerate(prs.slides,1):
 for sh in list(slide.shapes):
  if not sh.has_text_frame or not sh.text.strip() or sh.text.strip().isdigit():continue
  sizes=[r.font.size.pt for pp in sh.text_frame.paragraphs for r in pp.runs if r.font.size]
  if sizes and max(sizes)<=13 and sh.top>=Inches(6.25):
   removed.append({'page':page,'text':sh.text})
   slide.notes_slide.notes_text_frame.text+='\n【补充说明】'+sh.text
   slide.shapes._spTree.remove(sh._element)
# One concise note at the first complete AI-review overview replaces repeated disclaimers.
text(prs.slides[7],1.2,7.12,8,.19,'训练案例与评分为演示数据。',10,'727171')
# Place the meaning-bearing qualifier in the relevant body/caption rather than tiny footnotes.
for sh in prs.slides[32].shapes:
 if sh.has_text_frame and '导入 GPT、豆包' in sh.text:
  sh.text_frame.paragraphs[0].runs[0].text='导入支持语音与附件的 GPT、豆包等应用，'
for sh in prs.slides[34].shapes:
 if sh.has_text_frame and sh.text=='GitHub 公开仓库':sh.text_frame.paragraphs[0].runs[0].text='GitHub 仓库 · 简洁视图'
(ROOT/'story-v17-footnote-cleanup.json').write_text(json.dumps(removed,ensure_ascii=False,indent=2)+'\n')
prs.core_properties.title='AI职场沟通训练师｜第十七版 · 简介视频位置'
prs.save(ROOT/'AI-workplace-coach-story-v17.pptx');(ROOT/'story-v17-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
md=['# 第十七版讲述稿','','36页。第02页精简引入并预留视频位置；清理重复小字，补充说明保留在演讲备注。尚未嵌入MP4。','']
for r in rows:md.extend([f'## {r["page"]:02d}｜{r["title"]}','','讲述：'+r['speech'],'','转场：'+r['transition'],''])
(ROOT/'项目展示内容与讲述稿-第十七版.md').write_text('\n'.join(md));print('v17 built:36 pages, slide02 video slot')
