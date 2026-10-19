"""Revise uploaded v4 with input/effect pairs, early API setup and broader captures."""
import hashlib,json,math
from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.xmlchemy import OxmlElement

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets-v5'
SOURCE=ROOT/'source-story-v4-user.pptx'
prs=Presentation(SOURCE)
original=list(prs.slides)
rows=json.loads((ROOT/'story-v4-content.json').read_text())
row_by_part={s.part.partname:dict(row) for s,row in zip(original,rows)}
FONT='Noto Sans CJK SC';RED='C70019';INK='4C4948';MUTED='727171'
CAPTION='界面实拍｜案例、评分与分析为本机演示数据，非真实模型或业务效果实测'
review=json.loads((ASSETS/'primary-review.json').read_text())['review']
portrait=json.loads((ASSETS/'portrait-data.json').read_text())
assert portrait['sessionCount']==3 and portrait['sampleCount']==18

def text(sl,x,y,w,h,value,size=18,color=INK,bold=False):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True
 tf.margin_left=tf.margin_right=Inches(.01);tf.margin_top=Inches(.015);tf.margin_bottom=0
 for i,line in enumerate(value.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.space_after=Pt(3);p.line_spacing=1.15
  run=p.add_run();run.text=line;run.font.name=FONT;run.font.size=Pt(size);run.font.bold=bold;run.font.color.rgb=RGBColor.from_string(color)
  ea=OxmlElement('a:ea');ea.set('typeface',FONT);run._r.get_or_add_rPr().append(ea)
 return sh

def picture(sl,name,x,y,w,h):
 path=ASSETS/name
 with Image.open(path) as im:iw,ih=im.size
 scale=min(w/iw,h/ih);aw=iw*scale;ah=ih*scale
 return sl.shapes.add_picture(str(path),Inches(x+(w-aw)/2),Inches(y),width=Inches(aw),height=Inches(ah))

def prepare(sl,title,tab='practice'):
 for sh in list(sl.shapes):
  if sh==sl.shapes.title:continue
  sl.shapes._spTree.remove(sh._element)
 picture(sl,'nav-'+tab+'.png',.55,.99,8.9,.6)
 text(sl,.52,1.72,8.95,.6,title,27,INK,True)
 text(sl,.62,6.96,8.85,.2,CAPTION,9,MUTED)

def foot(sl,value):
 sh=text(sl,.62,6.53,8.85,.35,value,13,RED,True)
 sh.text_frame.paragraphs[0].alignment=PP_ALIGN.CENTER

def record(sl,title,body,speech,transition,point,seconds=30):
 row_by_part[sl.part.partname]={'title':title,'body':body,'speech':speech,'transition':transition,'point':point,'seconds':seconds,'appendix':False}

def insert_after(sl,part='第二部分  应用成效'):
 new=prs.slides.add_slide(prs.slide_layouts[2]);new.shapes.title.text=part
 from pptx.opc.packuri import PackURI
 new.part.partname=PackURI('/ppt/slides/slide'+str(1000+len(prs.slides))+'.xml')
 for p in new.shapes.title.text_frame.paragraphs:
  for r in p.runs:r.font.name=FONT;r.font.size=Pt(24);r.font.bold=True;r.font.color.rgb=RGBColor.from_string(INK)
 sid=prs.slides._sldIdLst[-1];prs.slides._sldIdLst.remove(sid)
 target=next(i for i,s in enumerate(prs.slides) if s==sl)
 prs.slides._sldIdLst.insert(target+1,sid)
 return new

from story_v5_demo import COMMANDS

# API introduction immediately follows the introduction's product overview.
s=insert_after(original[4]);title='接入模型 API，支撑连续对话与复盘。';prepare(s,title)
text(s,.72,2.35,8.6,.36,'入口在右上角“API 设置” · 可保存并切换多套配置',15,RED,True)
picture(s,'api-profiles.png',.65,2.87,5.02,3.43)
text(s,6.03,2.82,3.2,.35,'对话模型',15,RED,True);picture(s,'api-dialog-model.png',6.03,3.3,3.2,.58)
text(s,6.03,4.02,3.2,.35,'复盘模型',15,RED,True);picture(s,'api-review-model.png',6.03,4.5,3.2,.58)
text(s,6.03,5.38,3.2,.82,'支持 OpenAI 兼容服务商\n也可配置本机模型',15)
foot(s,'服务地址与模型可配置；截图采用无真实 Key 的展示配置。')
record(s,title,'配置服务地址、对话与复盘模型，可切换多套 OpenAI 兼容配置。','进入训练前，先看模型接入。项目通过API调用模型，支持保存和切换多套配置，也支持OpenAI兼容服务商和本机模型。左边是地址与配置入口，右边是对话和复盘模型。本页为无真实密钥的展示配置，不代表现场验证了服务商连接。','模型接好了，再带着刚才的交付任务进入训练。','指配置名称、Base URL、两种模型字段；不要展示或念出真实Key。',35)
row_by_part[original[4].part.partname]['transition']='正式练习前，先说明模型从哪里接入。'

# Broader screenshots carry multiple observations and more real UI context.
s=original[12];title='三场训练，18 次回应，留下两项沟通特征。';prepare(s,title,'portrait')
picture(s,'portrait-summary-and-traits.png',.62,2.4,6.65,4.08)
for y,head,body in [(2.7,'样本来自练习','3场训练 · 18次回应'),(3.85,'先推进，再补依据','观察跨场景重复出现'),(5.0,'区分承诺与边界','每项都保留原话来源')]:
 text(s,7.35,y,2.02,.68,head,17,RED,True);text(s,7.35,y+.69,2.02,.62,body,12,MUTED)
foot(s,'同屏展示累计摘要和两项特征，保留原页面的上下文。')
record(s,title,'扩大截图至累计摘要与两项沟通特征，保留三场18次回应的样本统计。','这次把截图范围扩大：上面是三场、18次回应的累计摘要，下面是两项反复出现的特征。它们分别关注判断依据和承诺边界，旁边保留原话来源入口。画像不是只给一句评价，而是把观察拆开，供用户逐项核对。','再看看这些观察如何转成优势和下一轮练法。','指样本统计、两项特征及各自的原话来源。',30)

s=original[13];title='已有优势和提升方向，都能继续展开。';prepare(s,title,'portrait')
text(s,.65,2.35,4.2,.35,'已有优势 · 两项',15,RED,True);text(s,5.15,2.35,4.2,.35,'提升方向 · 两项',15,RED,True)
picture(s,'portrait-strengths.png',.65,2.85,4.2,3.62);picture(s,'portrait-directions.png',5.15,2.85,4.2,3.62)
foot(s,'优势看责任与备选；方向看决策请求与证据口径。')
record(s,title,'扩大截图展示两项优势、两项提升方向与具体练习措施。','左边不只保留主动承担责任，也能看到提供备选方案的优势。右边把练习方向拆成两项：请求更明确，依据口径更可核查。每项都有解释和原话入口，用户可以只选其中一条带回下一轮。','如果对这些观察有疑问，可以直接展开来源。','左侧两项优势、右侧两项方向；只读标题，不逐字念正文。',25)

s=original[16];title='一份纪要，同时补齐人、项目和经验。';prepare(s,title)
text(s,.65,2.35,4.2,.35,'对象观察与记载语句',15,RED,True);text(s,5.15,2.35,4.2,.35,'项目背景与可复用经验',15,RED,True)
picture(s,'meeting-person-complete.png',.65,2.8,4.2,3.20);picture(s,'meeting-project-experience.png',5.15,2.8,4.2,3.20)
picture(s,'meeting-save-controls.png',.65,6.10,8.7,.35)
foot(s,'归属可以调整，依据可以展开，勾选后再保存到相应位置。')
record(s,title,'展示同一次纪要提取的人物、语录、项目与经验，以及保存入口。','同一份纪要可以提取几类结果：左边是对象观察和记载语句，右边是项目背景、行动项与经验。用户先核对归属和原文，再勾选保存。截图这次保留更多条目，能直接看出资料会分别进入哪里。','先看关于朱总的语录怎样继续用于训练。','左右分别指人物和项目/经验，最后指保存按钮。',30)

s=original[19];title='经验能导入、检索，也能继续积累。';prepare(s,title,'experiences')
picture(s,'experience-library-complete.png',.58,2.38,8.84,4.10)
foot(s,'原生页面保留添加、导入、导出、检索与多条经验卡片。')
record(s,title,'完整页面展示经验库的添加、文件导入/导出、搜索与多条经验。','经验库不只是一张卡片。页面可以添加经验，也支持文件导入、导出和检索；新训练会参考相关经验。这里保留控件和多条卡片，让观众同时看到入口与实际内容。接下来再看，日常补充资料能怎样更省步骤。','资料准备不必总靠表单，常用修改可以直接说。','指添加、导入、导出、搜索框和两条经验；格式细节按需展开。',25)

# Four concrete input/effect pairs make the natural-language workspace visible.
create=original[20]
edit=insert_after(create,'第三部分  亮点')
intensity=insert_after(edit,'第三部分  亮点')
experience=insert_after(intensity,'第三部分  亮点')
PAIR_SPECS=[
 ('create',create,'直接说新增谁，右边就出现新对象。','对象画像 · 新增王工','一段自然语言，完成对象的称呼、角色与关注点建档。','左边输入王工的角色和沟通特点，提交后，右边对象画像里就出现了王工。这里展示实际新增的对象卡片，而不只展示“已办理”提示。原来的表单方式仍然保留。','对象建好后，日常的新观察也能继续补进去。'),
 ('edit',edit,'一句新观察，同时补进画像与语录。','对象画像 · 追加观察与原话','“我觉得”保留为观察，明确说过的话记入语录。','左边说朱总更关注验证边界，并记录他今天说的话。右边可以看到新增观察和语录：观察没有覆盖旧画像，语录也保留原话。两种资料分别保存，供后续模拟参考。','除了补资料，这个入口还可以调整正在进行的训练。'),
 ('intensity',intensity,'说“增加追问强度”，训练设置随之更新。','沟通训练 · 本轮与下次生效','标准调整为深入，当前训练留下强度变更记录。','这次只输入增加追问强度。右边的训练状态已经改为深入追问，下面还保留标准到深入的变更记录。这一设置作用于本轮后续回应和下次训练；已有对话和评分不会被重写。','会后想到一条可复用的方法，也可以在这里收录。'),
 ('experience',experience,'随手说一条方法，直接进入经验库。','沟通经验库 · 新增经验','输入风险表达方法后，经验库生成带“自由输入”来源的条目。','左边随手记录一条风险沟通方法，右边经验库就新增了对应卡片，来源标为自由输入。新建对象、补画像、调强度和存经验，四种常用修改由同一个入口承接。','这些办理结果和训练记录都能留存，之后继续回看。'),
]
for key,s,title,destination,caption,speech,transition in PAIR_SPECS:
 tab=COMMANDS[key]['tab'];prepare(s,title,tab)
 text(s,.65,2.35,4.2,.35,'直接说 · 用户输入',14,RED,True);text(s,5.15,2.35,4.2,.35,destination,14,RED,True)
 text(s,.65,2.86,4.2,1.16,COMMANDS[key]['input'],17)
 picture(s,f'direct-{key}-input.png',.65,4.27,4.2,1.85)
 if key=='create':picture(s,'direct-create-effect.png',5.15,2.88,4.2,3.48)
 elif key=='edit':
  text(s,5.15,2.87,4.2,.32,'画像里追加的观察',12,MUTED);picture(s,'direct-edit-personality.png',5.15,3.29,4.2,1.20)
  text(s,5.15,4.65,4.2,.32,'语录中保留的原话',12,MUTED);picture(s,'direct-edit-quotes.png',5.15,5.05,4.2,1.22)
 elif key=='intensity':
  text(s,5.15,2.87,4.2,.64,'标准 → 深入',28,RED,True)
  picture(s,'direct-intensity-preference.png',5.15,3.73,4.2,1.03)
  text(s,5.15,5.00,4.2,.34,'当前训练的变更记录',13,MUTED)
  picture(s,'direct-intensity-log.png',5.15,5.51,4.2,.75)
 else:
  picture(s,'direct-experience-effect.png',5.15,2.88,4.2,2.77)
  picture(s,'direct-experience-receipt.png',5.15,5.75,4.2,.57)
 foot(s,caption)
 record(s,title,caption,speech,transition,'左边先读输入，再指真实输入框；右边看目的页面中的实际变化。自由输入区常驻页面底部。',30 if key!='intensity' else 25)

# Destination history now includes the active intensity demonstration as well as three reviews.
s=original[21];prepare(s,'训练与办理之后，结果都能继续回看。','history')
picture(s,'history.png',.65,2.4,8.7,3.63);picture(s,'export-actions.png',.65,6.12,8.7,.32)
foot(s,'训练记录保留原话与复盘，支持回看及 HTML、JSON、打印/PDF 导出。')
record(s,'训练与办理之后，结果都能继续回看。','三场已复盘训练和一次强度设置演示的进行中训练，均在实际记录中。','训练记录里可以看到完成的三场练习，以及刚才调整强度的进行中训练。原话、复盘和来源都能继续回看；有复盘的记录还能导出HTML、JSON或打印为PDF。','自然语言入口之外，原来的对象管理方式也完整保留。','指记录列表与导出入口，说明三场已复盘、一场正在训练。',20)

# Bring object maintenance and theme capabilities into the main deck, before the outcome summary.
obj=original[23];obj._element.attrib.pop('show',None);obj.shapes.title.text='第三部分  亮点'
prepare(obj,'对象也能用表单维护，新增、编辑和删除。','objects')
picture(obj,'objects-complete.png',.6,2.36,8.8,4.13)
foot(obj,'保留原表单、删除与语录分析；对象的目标、偏好和模拟边界分别维护。')
record(obj,'对象也能用表单维护，新增、编辑和删除。','自然语言和原表单并行；对象卡片保留编辑、删除和语录分析。','用户想精细调整时，仍然可以回到原表单。对象卡片提供编辑、语录分析和删除入口；既能快速补充，也能逐项核对目标与模拟边界。','功能可以适配不同沟通对象，界面也可以适配展示风格。','指新建、编辑画像、语录与分析、删除四个入口。',20)

theme=original[24];theme._element.attrib.pop('show',None);theme.shapes.title.text='第三部分  亮点'
for sh in theme.shapes:
 if sh.has_text_frame and '提问时按需打开' in sh.text:
  sh.text='视觉适配 / 公司展示与个人偏好'
  for run in sh.text_frame.paragraphs[0].runs:run.font.name=FONT;run.font.size=Pt(12);run.font.bold=True;run.font.color.rgb=RGBColor.from_string(RED)
for sl in [obj,theme]:
 for run in sl.shapes.title.text_frame.paragraphs[0].runs:run.font.name=FONT;run.font.size=Pt(24);run.font.bold=True;run.font.color.rgb=RGBColor.from_string(INK)
row_by_part[theme.part.partname].update({'appendix':False,'seconds':15,'speech':'默认企业红适合公司展示，同时保留森林绿、海洋蓝和鸢尾紫。切换会在本机记住，导出的报告也沿用所选主题。这里用四套实际界面快速带过。','transition':'回到当前交付与后续验证，结束这次介绍。','point':'指企业红默认主题和其余三套主题，不逐字读截图。'})
# Reorder the existing outcome summary after both newly visible maintenance pages.
summary=original[22];sid=next(x for x in prs.slides._sldIdLst if prs.part.related_slide(x.rId)==summary)
prs.slides._sldIdLst.remove(sid)
closing_index=next(i for i,sl in enumerate(prs.slides) if sl==original[25]);prs.slides._sldIdLst.insert(closing_index,sid)
row_by_part[summary.part.partname]['speech']='从模型接入，到一次训练与复盘，再到资料积累和直接说修改，主要功能都已通过实际界面串起来。已有测试验证流程；真实模型理解、评分质量和业务改善，仍需要在脱敏工作场景中继续试点。'
row_by_part[summary.part.partname]['transition']='让下一次关键沟通多一份准备，就是项目希望带来的价值。'
row_by_part[original[25].part.partname]['transition']='欢迎交流。'

content=[]
for i,sl in enumerate(prs.slides,1):
 row=dict(row_by_part[sl.part.partname]);row['page']=i;row['appendix']=False
 sl._element.attrib.pop('show',None)
 sl.notes_slide.notes_text_frame.text=f'【建议停留】{row["seconds"]}秒\n【本页一句话】{row["body"]}\n【看图指向】{row["point"] or "按页面顺序讲述"}\n【讲述稿】\n{row["speech"]}\n【转场】\n{row["transition"]}'
 for sh in list(sl.shapes):
  if sh.has_text_frame and sh.text.strip().isdigit() and sh.top>Inches(7):sl.shapes._spTree.remove(sh._element)
 if i not in [1,len(prs.slides)]:text(sl,.54,7.1,.45,.23,str(i).zfill(2),9,MUTED)
 content.append(row)

prs.core_properties.title='AI职场沟通训练师｜第五版 · 直接说输入效果对照与完整功能'
prs.core_properties.subject='API接入前置，四组自然语言输入/实际效果对照，截图保留更多上下文'
prs.save(ROOT/'AI-workplace-coach-story-v5.pptx')
(ROOT/'story-v5-content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
duration=sum(c['seconds'] for c in content)
coverage=[('API接入与多配置','6'),('场景、对象与目标','7'),('连续对话与三层解读','8–9'),('总分、六维与逐轮复盘','10–13'),('个人沟通画像及来源','14–16'),('纪要导入、项目背景与语录','17–20'),('经验库导入、导出、检索','21'),('直接说：新建对象','22'),('直接说：补画像与语录','23'),('直接说：调整本轮及下次强度','24'),('直接说：收录经验','25'),('训练记录与导出','26'),('对象表单维护与删除','27'),('四主题切换','28')]
md=['# AI职场沟通训练师｜第五版讲述稿','','基于本次上传的第四版修订，保留简介、案例、总分与多轮画像。新增API设置页放在第6页，四组直接说对照放在第22–25页。',
 '',f'共{len(content)}页，全部正常放映，无隐藏功能页。建议完整讲述约{round(duration/60,1)}分钟，另留现场操作与提问时间。',
 '', '实际界面通过隔离本机演示替身采集；对话、评分、分析和办理意图为演示数据，不代表真实模型或业务效果。API设置使用无真实Key的展示配置，未做真实服务商连接测试。',
 '', '## 功能覆盖','','| 功能 | 页码 |','| --- | --- |']
md.extend(f'| {name} | {pages} |' for name,pages in coverage)
md.extend(['','## 直接说的四个现场例子',''])
for key in ['create','edit','intensity','experience']:md.extend(['> '+COMMANDS[key]['input'],''])
for c in content:
 md.extend([f'## {c["page"]:02d}｜{c["title"]}','','**本页重点**：'+c['body'],'',f'**建议停留**：{c["seconds"]}秒','','**看图指向**：'+(c['point'] or '按页面顺序讲述'),'','**讲述稿**','',c['speech'],'','**转场**','',c['transition'],''])
(ROOT/'项目展示内容与讲述稿-第五版.md').write_text('\n'.join(md))
(ROOT/'story-v5-coverage.json').write_text(json.dumps(dict(coverage),ensure_ascii=False,indent=2)+'\n')
print('Built v5:',len(prs.slides),'pages;',duration,'seconds; API page 6; direct input/effect pages 22–25; no hidden pages.')
