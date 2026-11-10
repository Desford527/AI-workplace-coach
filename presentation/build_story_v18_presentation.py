"""Portable Skill evidence and GitHub closing page; voice demo is user-recorded later."""
from pathlib import Path
import json
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
ROOT=Path(__file__).resolve().parent;A=ROOT/'assets-v18';prs=Presentation(ROOT/'AI-workplace-coach-story-v17.pptx');rows=json.loads((ROOT/'story-v17-content.json').read_text())
def text(sl,x,y,w,h,s,size=18,color='4C4948',bold=False,url=None):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 for i,line in enumerate(s.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();r=p.add_run();r.text=line;r.font.name='Noto Sans CJK SC';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
  ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)
  if url:r.hyperlink.address=url
 return sh
def newpage(title):
 sl=prs.slides.add_slide(prs.slide_layouts[2])
 for sh in list(sl.shapes):
  if sh!=sl.shapes.title:sl.shapes._spTree.remove(sh._element)
 sl.shapes.title.text='第二部分  应用成效'
 for r in sl.shapes.title.text_frame.paragraphs[0].runs:r.font.name='Noto Sans CJK SC';r.font.size=Pt(24);r.font.bold=True;r.font.color.rgb=RGBColor.from_string('4C4948')
 text(sl,.55,1.02,9,.55,title,25,bold=True)
 sl.shapes.add_picture(str(A/'nav-objects.png'),Inches(.65),Inches(1.67),width=Inches(8.7))
 return sl
ids=[];newrows=[]
sl=newpage('先认识沟通对象，让追问更贴近实际工作。')
sl.shapes.add_picture(str(A/'object-roster.png'),Inches(.7),Inches(2.36),width=Inches(4.85))
text(sl,5.95,2.5,3.35,.4,'画像设定，影响模拟方式',19,'C70019',True)
text(sl,6.0,3.25,3.2,.85,'工作目标与判断标准\n决定优先追问什么。',18)
text(sl,6.0,4.42,3.2,.85,'表达风格与沟通习惯\n影响怎样问、怎样推进。',18)
text(sl,6.0,5.59,3.2,.85,'朱总、严工、客户代表\n也可新增自己的对象。',18)
ids.append(prs.slides._sldIdLst[-1])
newrows.append(dict(title='先认识沟通对象，让追问更贴近实际工作。',body='对象画像记录工作目标、关注点与表达习惯，为角色模拟提供参考。',point='对象画像标签、实际对象卡片，再指右侧三类设定如何影响模拟。',seconds=35,speech='配置好模型之后，先看对象画像。同样一份汇报，项目负责人可能关心交付和风险，技术专家可能更关心验证条件。这里可以维护对象的工作目标、判断标准和表达习惯，供AI选择追问重点与推进方式。可以使用现有的朱总、严工和客户代表，也可以新增自己的对象。它服务于工作场景模拟，不是给现实人物贴人格标签。',transition='画像不仅可以填写，也能从对方说过的话中逐步补充。',appendix=False))
sl=newpage('把对方说过的话，变成有依据的画像参考。')
text(sl,.75,2.35,4.0,.4,'记录语录',20,'C70019',True)
sl.shapes.add_picture(str(A/'quote-input.png'),Inches(.75),Inches(3.00),width=Inches(4.0))
text(sl,.8,4.68,3.9,1.1,'手动补充、导入会议纪要，\n或在“直接说”中添加观察与语录。',18,bold=True)
text(sl,.8,6.05,3.95,.5,'语录是原话，特征分析是推测。',17,'C70019',True)
sl.shapes.add_picture(str(A/'quote-analysis.png'),Inches(5.1),Inches(2.4),width=Inches(4.2))
text(sl,5.15,6.35,4.1,.4,'查看依据，也能生成可能的模拟表达。',15,'C70019',True)
ids.append(prs.slides._sldIdLst[-1])
newrows.append(dict(title='把对方说过的话，变成有依据的画像参考。',body='记录语录、分析有依据的沟通特征，并生成明确标注的模拟表达。',point='左侧是两条语录；右侧为实际界面的特征推测、原话依据与模拟表达。',seconds=40,speech='例如记录朱总的两句话：没有验证记录，先不要承诺交付；先把测试条件和边界说清楚。AI可以据此提出谨慎的特征推测，并保留原话依据，再生成可能的模拟表达。语录、推测和模拟台词分别标注，不混为一谈。后续还能通过会议纪要或直接说继续补充。画面里的分析来自本机演示替身；实际结果取决于模型和用户提供的资料。',transition='对象准备好之后，再选场景和目标，进入正式对话。',appendix=False))
for offset,sid in enumerate(ids):prs.slides._sldIdLst.remove(sid);prs.slides._sldIdLst.insert(4+offset,sid)
rows[3]['transition']='模型接好后，先认识本次要沟通的对象。'
rows[4:4]=newrows
for i,(sl,row) in enumerate(zip(prs.slides,rows),1):
 row['page']=i
 for sh in list(sl.shapes):
  if sh.has_text_frame and sh.text.strip().isdigit() and sh.top>Inches(7):sl.shapes._spTree.remove(sh._element)
 if i not in [1,len(rows)]:text(sl,.54,7.1,.45,.23,str(i).zfill(2),9,'727171')
 # Preserve prior detailed notes, updating only changed transitions and inserted pages.
 if i in [4,5,6]:sl.notes_slide.notes_text_frame.text=f'【讲述】\n{row["speech"]}\n【转场】\n{row["transition"]}'
prs.core_properties.title='AI职场沟通训练师｜第十八版 · 对象画像与语录'
prs.save(ROOT/'AI-workplace-coach-story-v18.pptx');(ROOT/'story-v18-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
md=['# 第十八版讲述稿','','38页。第05–06页新增对象画像与语录说明，放在API之后、正式训练之前。第02页视频占位及感谢页保留。','']
for r in rows:md.extend([f'## {r["page"]:02d}｜{r["title"]}','','讲述：'+r['speech'],'','转场：'+r['transition'],''])
(ROOT/'项目展示内容与讲述稿-第十八版.md').write_text('\n'.join(md));print('v18 built:38 pages; object portraits on 5–6')
