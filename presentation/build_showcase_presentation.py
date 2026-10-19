"""Build the editable corporate-template deck. Requires python-pptx (authoring only).
Screenshots use fictional presentation dialogue, never production model output.
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN,MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'AI-workplace-coach-showcase-v2.pptx'
prs=Presentation(ROOT/'company-template.pptx')
RED='C70019';INK='4C4948';MUTED='727171';PALE='FBF5F4';LINE='E7DAD7';WHITE='FFFFFF';FONT='Noto Sans CJK SC'
content=[]

def font(run,size=20,color=INK,bold=False):
 run.font.name=FONT;run.font.size=Pt(size);run.font.bold=bold;run.font.color.rgb=RGBColor.from_string(color)
 rpr=run._r.get_or_add_rPr()
 ea=rpr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}ea')
 if ea is None:ea=OxmlElement('a:ea');rpr.append(ea)
 ea.set('typeface',FONT)

def text(sl,x,y,w,h,value,size=20,color=INK,bold=False,align=None):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True
 tf.margin_left=tf.margin_right=Inches(.01);tf.margin_top=Inches(.015);tf.margin_bottom=0
 for i,line in enumerate(value.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.space_after=Pt(6);p.line_spacing=1.15
  if align is not None:p.alignment=align
  run=p.add_run();run.text=line;font(run,size,color,bold)
 return sh

def box(sl,x,y,w,h,fill=PALE,line=LINE,radius=True):
 sh=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string(fill)
 sh.line.color.rgb=RGBColor.from_string(line);sh.line.width=Pt(.7)
 if radius:sh.adjustments[0]=.08
 return sh

def label(sl,x,y,w,value,color=RED):return text(sl,x,y,w,.34,value,12,color,True)
def card(sl,x,y,w,h,title,body,number=None):
 box(sl,x,y,w,h)
 if number:text(sl,x+.2,y+.15,.6,.5,number,27,RED,True);offset=.8
 else:offset=.2
 text(sl,x+offset,y+.18,w-offset-.18,.48,title,18 if w<3 else 19,INK,True)
 sh=text(sl,x+.2,y+.74,w-.4,h-.82,body,16)
 for paragraph in sh.text_frame.paragraphs:paragraph.space_after=Pt(3);paragraph.line_spacing=1.1

def picture(sl,name,x,y,w,h):
 from PIL import Image
 path=ROOT/'assets-v2'/name
 with Image.open(path) as im:iw,ih=im.size
 ratio=iw/ih;target=w/h
 if ratio>target:
  actualw=w;actualh=w/ratio
 else:actualh=h;actualw=h*ratio
 return sl.shapes.add_picture(str(path),Inches(x+(w-actualw)/2),Inches(y),width=Inches(actualw),height=Inches(actualh))

def note(sl,title,body,speech):
 sl.notes_slide.notes_text_frame.text=speech+'\n\n【页面文字】\n'+body
 content.append({'title':title,'body':body,'speech':speech})

# Keep the supplied cover and closing, with original train banners and CRRC marks.
for index in (3,2,1):
 sid=prs.slides._sldIdLst[index];prs.part.drop_rel(sid.rId);prs.slides._sldIdLst.remove(sid)
cover=prs.slides[0];closing=prs.slides[1]
# Keep the original closing part out of python-pptx's sequential new-slide names.
from pptx.opc.packuri import PackURI
closing.part.partname=PackURI('/ppt/slides/slide999.xml')
for master in prs.slide_masters:
 for layout in [master,*master.slide_layouts]:
  for sh in layout.shapes:
   if sh.has_text_frame and '版权所有 2015' in sh.text:
    sh.text_frame.clear();r=sh.text_frame.paragraphs[0].add_run();r.text='AI赋能·智创未来  |  AI职场沟通训练师';font(r,8,MUTED)

def set_shape(sh,value,size,color=INK,bold=False):
 sh.text_frame.clear();sh.text_frame.word_wrap=True
 for i,line in enumerate(value.split('\n')):
  p=sh.text_frame.paragraphs[0] if i==0 else sh.text_frame.add_paragraph();p.space_after=Pt(3);r=p.add_run();r.text=line;font(r,size,color,bold)
for sh in cover.shapes:
 if not sh.has_text_frame:continue
 if 'AI应用成果发布模板' in sh.text:set_shape(sh,'AI职场沟通训练师',34,INK,True)
 elif '演讲人' in sh.text:set_shape(sh,'把下一次高压沟通，提前练一遍。',21,RED,True)
 elif sh.name=='文本占位符 3':set_shape(sh,'“AI赋能·智创未来”AI应用成果发布\n实际界面截图展示 · 第二版',14,MUTED)
 elif sh.name=='文本占位符 9':set_shape(sh,'项目汇报 / 技术评审 / 客户沟通 / 国际协作',11,MUTED)
note(cover,'AI职场沟通训练师','把下一次高压沟通，提前练一遍。\n项目汇报 / 技术评审 / 客户沟通 / 国际协作','大家好，今天介绍的是 AI职场沟通训练师。很多工作难题，卡在关键的一次沟通：事实已经掌握，话却没有说到对方关心的点上。我们想做的，就是给重要沟通加一次低成本的预演。')

def slide(part,kicker,title):
 sl=prs.slides.add_slide(prs.slide_layouts[2]);set_shape(sl.shapes.title,part,24,INK,True)
 label(sl,.52,1.06,8.9,kicker);text(sl,.52,1.48,8.95,.75,title,27,INK,True)
 text(sl,.54,7.1,.45,.23,str(len(content)+1).zfill(2),9,MUTED)
 return sl


CAPTION='界面实拍｜样例、评分及分析使用本机演示数据，非真实模型实测'

def shot(part,kicker,title,image,caption,speech,points=None):
 s=slide(part,kicker,title)
 if points:
  picture(s,image,.58,2.37,6.18,4.13)
  for i,(head,body) in enumerate(points):
   y=2.56+i*1.22;text(s,7.03,y,2.3,.4,head,17,RED,True);text(s,7.03,y+.47,2.3,.68,body,13,MUTED)
 else:picture(s,image,.55,2.32,8.9,4.12)
 text(s,.62,6.53,8.85,.35,caption,13,RED,True,PP_ALIGN.CENTER)
 text(s,.62,6.94,8.85,.2,CAPTION,9,MUTED)
 note(s,title,caption,speech)
 return s

shot('第一部分  项目简介','成果实拍 01 / 首页与工作区','打开项目，直接看到可用的训练入口。','home.png','沟通训练、对象画像、经验库、个人画像、训练记录都已接入。','这一页直接看产品。主页面已经串起训练、对象、经验和记录等入口。接下来我们沿着一个真实的操作流程，逐页看项目做成了哪些界面。所有截图均来自实际运行的本机产品，示例数据用于展示。')
shot('第一部分  项目简介','成果实拍 02 / 训练配置','对象、强度、目标和背景，一页准备好。','training-setup.png','选朱总、定目标、带入项目背景，再进入连续对话。','这里可以选择沟通对象和追问强度，并明确训练目标。导入纪要后形成的项目背景，也可以直接选入并继续编辑。用户在开场前就知道这次要推动什么事。')
shot('第一部分  项目简介','成果实拍 03 / 对象画像','同一份汇报，面对不同对象有不同关注点。','objects.png','朱总与严工已有不同角色；对象可以新增、编辑、删除。','对象卡片已经落到产品中。朱总是一位技术背景的项目负责人，严工侧重技术评审。用户可以维护各自关注点、沟通风格和模拟边界；添加与删除对象的入口也都保留。')
shot('第一部分  项目简介','成果实拍 04 / 语录与特征','把对方说过的话，变成有依据的观察。','quote-analysis.png','已记录语录、特征推测和模拟表达分别呈现。','这一页看语录分析的实际结果。系统分别展示依据原话推测的沟通特征，以及可能的模拟表达。原话、推测和模拟台词分开保存，避免把一次发言当成稳定人格结论。', [('原话有记录','用户可以持续补充对象说过的话。'),('推测有依据','每项特征可以展开引用。'),('模拟有标识','可能的表达不会冒充真实语录。')])
shot('第二部分  应用成效','成果实拍 05 / 连续对话','一句“差不多”，马上迎来下一轮追问。','conversation.png','完整上下文持续保留，追问围绕证据、交付范围与下一步。','截图展示一段虚构的项目汇报练习。用户说差不多、一直加班，朱总继续问哪些验证已经完成、具体交付什么范围。这里展示的连续对话、回应保存与上下文推进都来自实际产品流程。')
shot('第二部分  应用成效','成果实拍 06 / 原话三层解读','点开一句追问，看清它对应什么工作问题。','three-level.png','表面问题、核心关切、判断依据，分层展开。','原话下面可以展开三层解读：表面问了什么，可能关心什么，判断依据是什么。界面明确标为模拟推断，帮助理解工作语境，不将推测当成现实人物的心理事实。')

s=slide('第二部分  应用成效','成果实拍 07 / 本轮复盘','结束训练，就能回看总评与下一轮重点。')
picture(s,'review-summary.png',.6,2.4,8.8,1.96)
picture(s,'next-actions.png',.6,4.51,8.8,1.98)
text(s,.62,6.55,8.85,.34,'上方看本轮判断，下方看下一轮具体练什么。',13,RED,True,PP_ALIGN.CENTER);text(s,.62,6.94,8.85,.2,CAPTION,9,MUTED)
note(s,'结束训练，就能回看总评与下一轮重点。','总分与短总评；明确可执行的下一轮练习重点。','这两张截图分别来自同一轮复盘的开头与行动建议区。用户先看短总评，再看下一轮最需要练的几件事。截图中的分数为明确标注的演示数据，不作为真实模型评分或业务改善的证据。')
shot('第二部分  应用成效','成果实拍 08 / 六维评分','雷达图和分项得分，直接看到表达短板。','review-radar.png','六维雷达、分项得分和原话依据放在同一复盘中。','这里是已经做出来的六维可视化。左边雷达帮助快速浏览，右边列出六项得分，下面还能展开具体依据。它不是凭一句好坏评价，而是围绕结论、证据、诉求、风险、行动和协作逐项回看。图中的数值用于界面演示。')
shot('第二部分  应用成效','成果实拍 09 / 逐轮复盘','原回答和改进示范，就放在一起对照。','round-review.png','每轮保留原话、点评、六维依据与可直接练习的改进示范。','逐轮复盘把用户原话与改进示范并排放置。截图中可以看到，系统把差不多、一直加班，改成先说明承诺边界，再说核查安排和决策请求。使用者可以对照读一遍，然后再开一轮练习。')
s=slide('第二部分  应用成效','成果实拍 10 / 我的沟通画像','练过的原话，逐步形成自己的表达画像。')
picture(s,'portrait-summary.png',.65,2.4,8.7,1.23);picture(s,'portrait-evidence.png',.65,3.8,8.7,2.58)
text(s,.62,6.55,8.85,.34,'画像总结与原话证据放在一起，少量样本标为初步观察。',13,RED,True,PP_ALIGN.CENTER);text(s,.62,6.94,8.85,.2,CAPTION,9,MUTED)
note(s,'练过的原话，逐步形成自己的表达画像。','从训练原话总结特征与提升方向，支持回看证据；少量样本明确标为初步观察。','上图看画像摘要，下图看一条观察对应的原话证据。产品已经把个人表达特征、已有优势和练习方向接起来，同时提示样本局限。这些演示数据用于展示实际界面，不代表真实用户画像结论。')
shot('第二部分  应用成效','成果实拍 11 / 导入会议纪要','把真实工作资料，带进下一次练习。','meeting-input.png','支持粘贴、TXT、Markdown、DOCX；可先编辑脱敏再分析。','会议纪要的导入界面已经移到自由输入区上方。用户可以选择文件或粘贴正文，在本机先检查和脱敏，再交给当前启用的模型进行提取。截图中的纪要是虚构演示样例。')
shot('第二部分  应用成效','成果实拍 12 / 提取预览','提取结果带着原文依据，核对后再保存。','meeting-preview.png','人物归属可选、原文依据可展开、需要的条目可勾选。','这一页展示提取完成后的实际预览。对象观察、语录、项目背景和经验都可以逐项查看。人物和项目可以重新指定，原文依据可以展开，勾选后再保存。导入不是直接覆盖已有资料。')

s=slide('第二部分  应用成效','成果实拍 13 / 项目背景','纪要中的项目状态，已经能接回训练。')
label(s,.7,2.35,8.5,'从纪要中保存的项目背景');picture(s,'project-background.png',.65,2.79,8.7,1.18)
label(s,.7,4.03,8.5,'训练页直接引用，并可继续编辑');picture(s,'project-context.png',.65,4.44,8.7,1.91)
text(s,.62,6.56,8.85,.34,'项目背景可复用；本轮训练冻结当前内容，旧记录保留。',13,RED,True,PP_ALIGN.CENTER);text(s,.62,6.94,8.85,.2,CAPTION,9,MUTED)
note(s,'纪要中的项目状态，已经能接回训练。','纪要中保存项目背景；训练页选择项目并编辑本次引用内容。','上图是保存后的项目背景，下图是训练页引用它的实际位置。背景可以继续补充、精简或脱敏，训练冻结当前版本。项目资料以后更新，也不会改写过去那轮训练的依据。')
shot('第三部分  亮点','成果实拍 14 / 沟通经验库','通用方法和自己的经验，终于有地方积累。','experience-library.png','支持搜索、手工添加、文件导入、导出和训练引用。','经验库已经内置通用职场沟通方法，并支持用户添加和导入。截图展示真实页面中的搜索与卡片。用户不需要每次从零组织思路，可以把适用的方法留给下一次练习。')
shot('第三部分  亮点','成果实拍 15 / 经验来源','一条新经验，可以追溯到它来自哪次会议。','experience-source.png','纪要提炼的经验保留原文依据，可回看来源纪要。','这一张放大看新收录的经验。它来自刚才的演示纪要，有明确的原文依据，也能回到来源会议。这样既能复用方法，也方便判断它适用在什么场景，避免把一次讨论机械推广到所有情况。', [('有可复用方法','说明验证边界，再提出承诺。'),('有来源依据','保留支持经验的纪要原文。'),('有适用边界','训练时参考，仍需结合实际。')])
s=slide('第三部分  亮点','成果实拍 16 / 自由输入','说完想改什么，界面直接列出办理结果。')
label(s,.7,2.33,8.5,'用户直接输入的一句话');picture(s,'free-input-command.png',.65,2.77,8.7,1.18)
label(s,.7,4.05,8.5,'保存后的实际办理结果');picture(s,'free-saved-result.png',.65,4.49,8.7,1.81)
text(s,.62,6.55,8.85,.34,'补充画像、追加语录、调整强度，一次输入完成多项修改。',13,RED,True,PP_ALIGN.CENTER);text(s,.62,6.94,8.85,.2,CAPTION,9,MUTED)
note(s,'说完想改什么，界面直接列出办理结果。','上图为提交的自然语言命令，下图为保存后的三项办理结果。','这一页把输入和结果都放大。用户一句话补充朱总的观察和原话，同时要求加深追问，系统分别列出保存了哪些变化。采集截图时已经通过真实界面点击提交并保存，演示替身只提供结构化解析结果，应用功能本身未改动。')

s=slide('第三部分  亮点','成果实拍 17 / 记录与导出','训练结束，记录和复盘都能带走。')
label(s,.7,2.34,8.5,'训练记录随时恢复与回看');picture(s,'history.png',.65,2.78,8.7,2.75)
label(s,.7,5.54,8.5,'再练一次，或导出分享与复查');picture(s,'export-actions.png',.65,6.02,8.7,.44)
text(s,.62,6.61,8.85,.28,'支持同场景再练、HTML、完整 JSON、打印 / PDF。',13,RED,True,PP_ALIGN.CENTER);text(s,.62,6.98,8.85,.17,CAPTION,9,MUTED)
note(s,'训练结束，记录和复盘都能带走。','训练记录可回看和恢复；支持再练、HTML、完整JSON、打印/PDF。','训练记录可以恢复和回看，复盘也可以导出。这里保留同场景再练、选择新场景、导出HTML、完整JSON以及打印PDF等入口。截图采集过程中实际点击并验证了HTML导出，历史记录也来自这次完整的演示流程。')

s=slide('第三部分  亮点','成果实拍 18 / 四套主题','公司演示用企业红，日常练习也有自己的颜色。')
for x,y,name,title in [(.63,2.34,'corporate','企业红 · 默认'),(5.14,2.34,'forest','森林绿'),(.63,4.48,'ocean','海洋蓝'),(5.14,4.48,'violet','鸢尾紫')]:
 picture(s,'theme-'+name+'.png',x,y,4.22,1.76);label(s,x,y+1.77,4.22,title)
text(s,.62,6.73,8.85,.25,'四套主题均已接入，切换会记住本机选择。',12,RED,True,PP_ALIGN.CENTER)
text(s,.62,7.0,8.85,.15,'实际产品主题截图；展示资料为本机虚构演示。',8,MUTED)
note(s,'公司演示用企业红，日常练习也有自己的颜色。','企业红、森林绿、海洋蓝、鸢尾紫；默认企业红，切换记住本机选择。','最后这页并排展示同一产品的四套实际主题。默认使用公司的企业红，原先喜欢的绿色保留，还提供蓝色和紫色。界面在公司展示与日常练习之间可以直接切换。')

for sh in closing.shapes:
 if sh.has_text_frame and '感谢观看' in sh.text:set_shape(sh,'让每一次表达，\n都推动事情向前。',30,INK,True)
 elif sh.has_text_frame:set_shape(sh,'AI职场沟通训练师  |  感谢观看',17,RED,True)
last=prs.slides._sldIdLst[1];prs.slides._sldIdLst.remove(last);prs.slides._sldIdLst.append(last)
note(closing,'让每一次表达，都推动事情向前。','把下一次高压沟通，提前练一遍。感谢观看。','以上展示的是已经做出来的产品界面与可操作的流程。下一步用脱敏的真实场景开展试点，再检验模型理解质量和实际使用效果。把下一次高压沟通，提前练一遍。谢谢大家。')
prs.core_properties.title='AI职场沟通训练师｜实际成果截图展示 第二版'
prs.core_properties.subject='18页功能截图展示，20页含封面封底；附逐页讲述稿'
prs.core_properties.author='项目展示材料'
prs.core_properties.keywords='AI,职场沟通,中国中车,产品截图,项目成果'
prs.save(OUT)
import json
(ROOT/'showcase-v2-content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md=['# AI职场沟通训练师｜截图增强版讲述稿','','共20页，其中18页展示实际产品截图。基于应用v5.0.15，未修改应用功能。案例、分数和分析由隔离的本机演示替身驱动，经过产品原有校验并完成真实按钮流程，不代表真实模型或业务实测效果。建议讲述8–10分钟，可按时间跳过部分细节页。','']
for i,item in enumerate(content,1):md.extend([f'## {i:02d}｜{item["title"]}','','**页面要点**','',item['body'],'','**讲述稿**','',item['speech'],''])
(ROOT/'项目展示内容与讲述稿-截图增强版.md').write_text('\n'.join(md),encoding='utf-8')
print('Built',OUT.name,'slides:',len(prs.slides),'screenshot pages:',len(prs.slides)-2)
