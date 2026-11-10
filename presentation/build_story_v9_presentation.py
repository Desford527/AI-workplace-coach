"""Shorten context to one page; show the real API entry above settings details."""
from pathlib import Path
import json
from PIL import Image
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
from pptx.enum.shapes import MSO_SHAPE
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'assets-v9';OUT.mkdir(exist_ok=True)
prs=Presentation(ROOT/'AI-workplace-coach-story-v8.pptx');rows=json.loads((ROOT/'story-v8-content.json').read_text())
def text(sl,x,y,w,h,s,size=18,color='4C4948',bold=False):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True
 tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 r=tf.paragraphs[0].add_run();r.text=s;r.font.name='Noto Sans CJK SC';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
 ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)
 return sh
def card(sl,y,title,body):
 sh=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(.65), Inches(y), Inches(8.7), Inches(1.12));sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string('FBF6F4');sh.line.color.rgb=RGBColor.from_string('EADBD7')
 text(sl,.85,y+.19,1.9,.36,title,18,'C70019',True);text(sl,2.8,y+.17,6.25,.72,body,17)
sl=prs.slides[1]
for sh in list(sl.shapes):
 if sh!=sl.shapes.title:sl.shapes._spTree.remove(sh._element)
text(sl,.55,1.12,8.9,.65,'把关键沟通，从临场应对变成提前练习。',26,bold=True)
card(sl,2.12,'工作需要','汇报进度、评审方案、协调客户，都要把事实讲清楚，让对方能决定。')
card(sl,3.47,'典型难点','问：“周五能交付吗？”\n答：“基本差不多，大家一直在加班……”')
card(sl,4.82,'项目做法','用 AI 连续追问 → 六维复盘 → 积累画像与经验，练清判断、依据和请求。')
text(sl,.75,6.3,8.5,.4,'从一次向朱总汇报交付的任务，看它怎样帮助沟通。',19,'C70019',True)
rows[1].update(title='把关键沟通，从临场应对变成提前练习。',body='工作要做决定，表达却容易停在模糊状态；用AI练习、复盘和积累补齐判断、依据与请求。',speech='项目汇报、技术评审和客户协调，都要让对方听清事实并做出决定。但一句基本差不多、大家一直在加班，仍然回答不了周五能不能交付。这个项目让用户先接受AI追问，再对照六维复盘，把画像与经验留给下一次。接下来就沿一次向朱总汇报交付的任务，看看它怎么用。',point='按工作需要、典型难点、项目做法三行讲，每行只讲一句。',transition='先看完整首页，建立对产品的整体印象。',seconds=40)
api=prs.slides[5]
for sh in list(api.shapes):
 if sh.has_text_frame and '入口在右上角' in sh.text:api.shapes._spTree.remove(sh._element)
im=Image.open(ROOT/'assets-v8/home-full.png');im.crop((0,0,im.width,260)).save(OUT/'api-entry-header.png')
api.shapes.add_picture(str(OUT/'api-entry-header.png'),Inches(.65),Inches(1.64),width=Inches(8.7))
rows[5]['point']='先指上方首页截图右上角的「API 设置」，再指下方配置名称、Base URL与两种模型字段。首页入口图为未配置状态；下方为无真实Key的展示配置。'
rows[5]['speech']='先看上方首页顶栏，API设置就在右上角。点击这个按钮，就进入下方展示的配置界面。这里可以保存和切换多套配置，分别设置对话与复盘模型，支持OpenAI兼容服务商和本机模型。上图用于定位入口，下图是无真实密钥的展示配置。'
# Remove two redundant introduction slides; the overview now follows the single background page.
for idx in [3,2]:
 sid=prs.slides._sldIdLst[idx];prs.part.drop_rel(sid.rId);prs.slides._sldIdLst.remove(sid);rows.pop(idx)
for i,(slide,row) in enumerate(zip(prs.slides,rows),1):
 row['page']=i
 for sh in list(slide.shapes):
  if sh.has_text_frame and sh.text.strip().isdigit() and sh.top>Inches(7):slide.shapes._spTree.remove(sh._element)
 if i not in [1,len(rows)]:text(slide,.54,7.1,.45,.23,str(i).zfill(2),9,'727171')
 slide.notes_slide.notes_text_frame.text=f'【建议停留】{row["seconds"]}秒\n【本页一句话】{row["body"]}\n【看图指向】{row["point"]}\n【讲述稿】\n{row["speech"]}\n【转场】\n{row["transition"]}'
prs.core_properties.title='AI职场沟通训练师｜第九版 · 精简背景与API入口定位'
prs.save(ROOT/'AI-workplace-coach-story-v9.pptx')
(ROOT/'story-v9-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
md=['# 第九版讲述稿','','共28页。背景介绍合并为第2页，第3页首页全貌，第4页API入口及配置。其他功能顺序不变。','']
for r in rows:md.extend([f'## {r["page"]:02d}｜{r["title"]}','','讲述：'+r['speech'],'','转场：'+r['transition'],''])
(ROOT/'项目展示内容与讲述稿-第九版.md').write_text('\n'.join(md))
print('v9 built: 28 pages, overview 3, API 4')
