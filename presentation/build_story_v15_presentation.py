"""Portable Skill evidence and GitHub closing page; voice demo is user-recorded later."""
from pathlib import Path
import json
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
ROOT=Path(__file__).resolve().parent;A=ROOT/'assets-v15';prs=Presentation(ROOT/'AI-workplace-coach-story-v13.pptx');rows=json.loads((ROOT/'story-v13-content.json').read_text())
def text(sl,x,y,w,h,s,size=18,color='4C4948',bold=False,url=None):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 for i,line in enumerate(s.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();r=p.add_run();r.text=line;r.font.name='Noto Sans CJK SC';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
  ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)
  if url:r.hyperlink.address=url
 return sh
from pptx.enum.shapes import MSO_SHAPE

def page(title):
 sl=prs.slides.add_slide(prs.slide_layouts[2])
 for sh in list(sl.shapes):
  if sh!=sl.shapes.title:sl.shapes._spTree.remove(sh._element)
 sl.shapes.title.text='第三部分  复用与推广'
 for r in sl.shapes.title.text_frame.paragraphs[0].runs:r.font.name='Noto Sans CJK SC';r.font.size=Pt(24);r.font.bold=True;r.font.color.rgb=RGBColor.from_string('4C4948')
 text(sl,.55,1.02,9,.55,title,25,bold=True)
 return sl

def box(sl,x,y,w,h,label,image=None):
 if image and image.exists():
  from PIL import Image
  iw,ih=Image.open(image).size;scale=min(w/iw,h/ih);ww,hh=iw*scale,ih*scale
  sl.shapes.add_picture(str(image),Inches(x+(w-ww)/2),Inches(y),width=Inches(ww),height=Inches(hh));return
 sh=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string('FAF7F5');sh.line.color.rgb=RGBColor.from_string('EADBD7')
 text(sl,x+.2,y+h/2-.25,w-.4,.6,label,17,'727171')

sl=page('项目已封装为 Skill，导入 AI 即可开展沟通训练。')
text(sl,.75,2.0,8.5,.85,'导入 GPT、豆包等支持语音的 AI 应用，\n设置对象与背景，即可开展实时对话。',22,bold=True)
box(sl,1.0,3.35,8.0,2.65,'')
play=sl.shapes.add_shape(MSO_SHAPE.OVAL,Inches(4.52),Inches(3.92),Inches(.96),Inches(.96));play.fill.solid();play.fill.fore_color.rgb=RGBColor.from_string('C70019');play.line.fill.background();play.name='VIDEO_BUTTON_REPLACE_HERE'
tri=sl.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE,Inches(4.86),Inches(4.22),Inches(.32),Inches(.36));tri.rotation=90;tri.fill.solid();tri.fill.fore_color.rgb=RGBColor.from_string('FFFFFF');tri.line.fill.background();tri.name='VIDEO_PLAY_ICON'
text(sl,2.2,5.15,5.6,.45,'海外客户实时对话演示',22,bold=True)
text(sl,1.1,6.3,7.8,.4,'已预留视频播放按钮位置，可在 PowerPoint 中替换或关联已录视频。',12,'727171')
text(sl,.75,6.88,8.5,.18,'语音与附件指令支持取决于所用AI应用；本页不预设所有平台兼容。',9,'727171')
skillrow=dict(title='项目已封装为Skill，导入AI即可开展沟通训练。',body='介绍导入GPT、豆包等AI应用后的实时沟通用途，预留已录视频的播放按钮位置。',point='先讲导入和实时交流，再点击自己插入的视频播放按钮。',seconds=25,speech='我把本项目的核心训练方法整理成了Skill。把它导入GPT、豆包等支持语音和附件指令的AI应用，设置沟通对象与背景，就可以开展实时对话。下面播放我已经录好的海外客户交流演示。',transition='通话结束后，获取Skill的AI还可以根据实际对话生成这样的复盘报告。',appendix=False)
sl=page('获取 Skill 的 AI，也能生成沟通复盘报告。')
text(sl,.7,1.75,4.25,.32,'实际对话 → 总评与逐轮分析',15,'C70019',True)
text(sl,5.1,1.75,4.25,.32,'沟通评分 → 英语反馈与改进表达',15,'C70019',True)
box(sl,.65,2.18,4.25,4.65,'待嵌入报告截图 1',A/'report-1.png')
box(sl,5.1,2.18,4.25,4.65,'待嵌入报告截图 2',A/'report-2.png')
text(sl,.75,6.98,8.5,.18,'用户实际GPT演示报告：依据两轮英文交流生成，训练评分不代表标准化英语能力测评。',9,'727171')
reportrow=dict(title='获取Skill的AI，也能生成沟通复盘报告。',body='用用户提供的两张实际报告截图展示总评、逐轮分析、评分和英语改进结果。',point='左边展示总评与原话，右边展示沟通评分与英语表达建议。',seconds=30,speech='这是这次真实演示生成的报告。它回到实际说过的原话，给出训练总评、逐轮分析、沟通评分和英语表达反馈。说明这套训练方法可以随Skill一起迁移到支持相关指令的AI应用里，而不仅停留在网页中。',transition='项目和Skill都已放到GitHub，欢迎大家下载体验。',appendix=False)
sl=page('项目已公开发布，欢迎下载体验。')
url='https://github.com/Desford527/AI-workplace-coach'
box(sl,.7,1.9,8.6,4.2,'待嵌入 GitHub 仓库首页截图',A/'github-styled.png')
text(sl,.8,6.28,8.4,.42,'github.com/Desford527/AI-workplace-coach',19,'C70019',True,url)
text(sl,.8,6.87,8.4,.22,'项目源码 · 本地应用 · Skill · 演示资料｜仓库实际内容简洁视图',11)
gitrow=dict(title='项目已公开发布，欢迎下载体验。',body='倒数第二页用GitHub仓库实拍和链接邀请观众下载。',point='仓库首页截图与可点击链接。',seconds=20,speech='本项目已经在GitHub公开，源码、本地应用、Skill和演示资料都可以获取，欢迎大家下载体验。',transition='谢谢大家。',appendix=False)
# Keep the original thank-you slide as the absolute last slide.
closing=prs.slides._sldIdLst[32];prs.slides._sldIdLst.remove(closing);prs.slides._sldIdLst.append(closing)
rows=rows[:32]+[skillrow,reportrow,gitrow,rows[-1]]
for i,(slide,row) in enumerate(zip(prs.slides,rows),1):
 row['page']=i
 if i in [33,34,35]:text(slide,.54,7.1,.45,.23,str(i).zfill(2),9,'727171')
 if i!=36:slide.notes_slide.notes_text_frame.text=f'【讲述】\n{row["speech"]}\n【转场】\n{row["transition"]}'
missing=[n for n in ['report-1.png','report-2.png','github-styled.png'] if not (A/n).exists()]
suffix='-draft' if missing else ''
prs.core_properties.title='AI职场沟通训练师｜第十五版 · Skill演示、报告与GitHub'
prs.save(ROOT/f'AI-workplace-coach-story-v15{suffix}.pptx');(ROOT/'story-v15-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('Built 36 slides. Missing original assets:',missing)
