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
OUT=ROOT/'AI-workplace-coach-presentation-v5.0.15.pptx'
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
 path=ROOT/'assets'/name
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
 elif sh.name=='文本占位符 3':set_shape(sh,'“AI赋能·智创未来”AI应用成果发布\n项目成果展示 · 2026年10月',14,MUTED)
 elif sh.name=='文本占位符 9':set_shape(sh,'项目汇报 / 技术评审 / 客户沟通 / 国际协作',11,MUTED)
note(cover,'AI职场沟通训练师','把下一次高压沟通，提前练一遍。\n项目汇报 / 技术评审 / 客户沟通 / 国际协作','大家好，今天介绍的是 AI职场沟通训练师。很多工作难题，卡在关键的一次沟通：事实已经掌握，话却没有说到对方关心的点上。我们想做的，就是给重要沟通加一次低成本的预演。')

def slide(part,kicker,title):
 sl=prs.slides.add_slide(prs.slide_layouts[2]);set_shape(sl.shapes.title,part,24,INK,True)
 label(sl,.52,1.06,8.9,kicker);text(sl,.52,1.48,8.95,.75,title,27,INK,True)
 text(sl,.54,7.1,.45,.23,str(len(content)+1).zfill(2),9,MUTED)
 return sl

s=slide('第一部分  项目简介','一个很熟悉的工作现场','汇报前最怕的，往往是这一句。')
box(s,.6,2.52,8.8,1.25,RED,RED);text(s,.88,2.72,8.2,.85,'“现在到底能不能交付？\n你需要我决定什么？”',25,WHITE,True)
label(s,.68,4.12,2,'你的回答');text(s,.68,4.52,8.5,.65,'“基本都差不多了，大家一直在加班……”',23)
for x,head,body in [(.65,'判断说不清','用“应该”代替判断'),(3.68,'证据拿不出','用“努力”代替事实'),(6.72,'请求落不下','只说“帮忙协调”')]:
 text(s,x,5.67,2.65,.42,head,19,RED,True);text(s,x,6.18,2.65,.4,body,14,MUTED)
note(s,'汇报前最怕的，往往是这一句。','朱总：现在到底能不能交付？你需要我决定什么？\n我：基本都差不多了，大家一直在加班……\n判断说不清｜证据拿不出｜请求落不下','先请大家想象一个场景：周例会上，朱总问你能不能交付。你说大家很辛苦、项目差不多了，但对方还是继续追问。问题往往不在于态度，而在于判断、证据和请求没有对齐。这就是这个项目切入的真实场景。')

s=slide('第一部分  项目简介','把表达练习放到任务里','从“准备说什么”，走到“当场说得出来”。')
for x,num,title,body in [(.6,'01','选对象与场景','明确这次要和谁聊，\n要推动什么事。'),(5.1,'02','进入连续对话','AI 根据角色与上下文\n追问，可调强度。')]:card(s,x,2.55,4.3,1.65,title,body,num)
for x,num,title,body in [(.6,'03','查看六维复盘','看原话、找依据，\n对照改进示范再练。'),(5.1,'04','沉淀画像与经验','把语录、纪要和复盘\n留给下一次沟通。')]:card(s,x,4.47,4.3,1.65,title,body,num)
text(s,.7,6.44,8.6,.38,'4 类场景  ·  六维 AI 评分  ·  原话三层解读',16,RED,True,PP_ALIGN.CENTER)
note(s,'从准备到开口，形成一个完整闭环。','选对象与场景 → 连续对话 → 六维复盘 → 画像与经验沉淀\n4类场景：项目汇报、技术评审、客户沟通、国际协作。','整个流程可以用四步理解。先把人和事选清楚，再真正开口练。对话结束后，系统会把每一轮原话、评分依据和改进示范放在一起。练过的内容会逐步形成个人画像和可复用经验，让下一次练习有积累。')

s=slide('第一部分  项目简介','已经可以本地启动的产品','选对象、带背景，开始一场有目标的练习。')
picture(s,'home.png',.55,2.35,8.9,4.18)
text(s,.7,6.55,8.6,.32,'朱总：项目负责人  ·  重证据、看边界、要闭环',15,RED,True,PP_ALIGN.CENTER)
note(s,'选对象、带背景，开始一场有目标的练习。','朱总：项目负责人。\n围绕工作目标、关注点、语录和专业背景模拟追问。\n可选场景、项目背景与追问强度，支持 OpenAI 兼容服务商。','这是目前可运行的实际界面。以演示对象朱总为例，他是一位技术背景的项目负责人，比较重视证据、风险边界和行动闭环。用户可以选场景、带入项目背景、调节追问强度。模型调用沿用已有 API 能力，支持 OpenAI 兼容服务商。截图仅展示产品界面，没有进行真实模型效果测试。')

s=slide('第二部分  应用成效','同一个问题，两种回答','周五能不能交付？先把话说到点上。')
card(s,.6,2.55,4.25,3.47,'一套糟糕的回答','基本都差不多了，大家最近一直在加班。周五交付应该没问题。')
box(s,5.1,2.55,4.3,3.47,WHITE,RED);label(s,5.35,2.78,3.8,'一套更有效的回答');text(s,5.35,3.32,3.8,2.35,'目前还不能承诺周五整机交付。常温验证已通过，高温验证尚未完成。\n我负责今天下班前补齐验证计划；请您确认台架优先级，再确定可交付范围。',18)
text(s,.7,6.22,8.6,.38,'明确判断  +  已知事实  +  未知边界  +  具体请求',18,RED,True,PP_ALIGN.CENTER)
text(s,.7,6.73,8.6,.22,'虚构演示案例；其中状态、时间与安排均非真实项目结论。',10,MUTED)
note(s,'同一个交付问题，两种回答。','糟糕：基本都差不多了，大家最近一直在加班。周五交付应该没问题。\n优秀：目前还不能承诺周五整机交付。常温验证已通过，高温验证尚未完成。我负责今天下班前补齐验证计划；请您确认台架优先级，再确定可交付范围。\n关键：明确判断、已知事实、未知边界、具体请求。\n本页为虚构演示。','这一页可以现场读两种回答。第一种听起来很积极，但领导仍然无法判断风险；第二种没有把话说满，却把判断、事实、未知项和请求说清楚了。演示重点是表达如何支持决策，不能把本页虚构的验证状态当成真实项目数据。')

s=slide('第二部分  应用成效','连续追问，让模糊表达显形','一句“应该没问题”，接下来会发生什么？')
# Crop the original screenshot in the slide, preserving the product's actual chat layout.
from PIL import Image
path=ROOT/'assets/conversation-full.png'
with Image.open(path) as im:iw,ih=im.size
crop_fraction=min(1,iw/1.93/ih)
label(s,.72,2.34,8.5,'朱总：项目负责人  |  项目进度汇报');picture(s,'conversation-full.png',.65,2.85,8.7,3.92)
text(s,.65,6.93,8.7,.15,'真实产品界面，填入虚构演示对话；不代表真实模型输出质量。',9,MUTED)
note(s,'一句应该没问题，接下来会发生什么？','朱总继续追问：哪些验证已经关闭，哪些还没关闭？周五交付的具体范围是什么？\n练习重点：先回答当前问题，再给证据、边界与下一步。\n截图中的对话为虚构演示数据。','连续对话的价值在这里：一句差不多，并不会让讨论自然结束。系统会根据前面的表达继续追问，让问题暴露在练习中。我们希望使用者逐步养成一个习惯：先回答当前问题，再给必要的证据、边界和下一步，而不是堆积更多背景。截图内对话是为展示产品布局填入的虚构示例。')

s=slide('第二部分  应用成效','每轮都有依据，每次都有改法','找到最该改的一点，再说一遍。')
for x,y,num,title,body in [(.65,2.5,'01','结论清晰','有没有先回答关键问题？'),(5.12,2.5,'02','证据具体','有没有可核实的事实？'),(.65,3.65,'03','诉求对齐','是否提出可决策的请求？'),(5.12,3.65,'04','边界与风险','是否说明未知项和影响？'),(.65,4.8,'05','下一步行动','是否明确责任人与时间？'),(5.12,4.8,'06','理解与协作','是否回应对方真正关切？')]:
 box(s,x,y,4.22,.96);text(s,x+.16,y+.14,.5,.5,num,24,RED,True);text(s,x+.8,y+.12,3.25,.34,title,17,INK,True);text(s,x+.8,y+.53,3.25,.29,body,13,MUTED)
text(s,.72,6.15,8.6,.55,'每轮总分与原话依据  /  逐轮点评与改进示范\n原话三层解读  /  长期沟通画像',16,RED,True,PP_ALIGN.CENTER)
note(s,'找到最该改的一点，再说一遍。','六维：结论清晰、证据具体、诉求对齐、边界与风险、下一步行动、理解与协作。\n每轮总分与原话依据；逐轮点评与改进示范；原话三层解读；长期沟通画像。','复盘覆盖六个维度，而且评分必须有本轮原话依据。用户可以看每轮总分、具体点评和改进示范，也能看到对方原话的表面问题、核心关切和判断依据。评分是训练反馈，不是经验证的能力测量；更有价值的是找到下一轮能实际改动的一点。')

s=slide('第二部分  应用成效','让真实工作资料进入训练','一份会议纪要，变成下一轮练习的底稿。')
box(s,.65,2.5,8.7,1.22);label(s,.9,2.68,8.2,'纪要摘录 · 虚构演示');text(s,.9,3.03,8.15,.45,'朱总：“没有验证记录，先不要承诺交付。”',21,INK,True)
for x,title,body in [(.65,'对象画像与语录','记录关注点与记载语句\n区分观察和特征推测'),(3.65,'项目背景与行动项','整理现状、风险与决议\n留下责任人与时间点'),(6.65,'沟通经验库','提炼可复用方法\n供新训练参考')]:card(s,x,4.08,2.7,1.8,title,body)
text(s,.75,6.28,8.5,.38,'原文依据可展开  →  人物与项目归属可核对  →  勾选后保存',16,RED,True,PP_ALIGN.CENTER)
text(s,.75,6.76,8.5,.22,'支持粘贴、TXT、Markdown、DOCX；入口位于“想改什么，直接说”的上方。',10,MUTED)
note(s,'一份会议纪要，变成下一轮练习的底稿。','会议纪要可提取：对象观察与语录、项目背景与行动项、可复用沟通经验。\n先看原文依据，再核对人物和项目归属，最后勾选保存。\n支持粘贴、TXT、Markdown、DOCX；入口已移至自由输入框上方。','很多沟通信息已经存在于真实会议纪要里。这个入口可以把它们整理成三类训练资料：对象画像和语录、项目背景和行动项、可复用经验。每项都有可展开的原文依据，人物和项目归属可以调整，核对后再保存。纪要记载不等于录音逐字稿，特征推测也不等于确定人格。')

s=slide('第二部分  应用成效','成果边界说清楚，试点才有方向','可运行的原型，已经具备完整训练闭环。')
box(s,.65,2.55,3.2,3.55,RED,RED);text(s,.93,2.88,2.65,1.2,'68',72,WHITE,True);text(s,.95,4.18,2.6,.48,'项后端测试通过',20,WHITE,True);text(s,.95,4.94,2.6,.85,'本机替身验证协议与流程\n不代表真实模型效果',13,WHITE)
for y,title,body in [(2.57,'完整流程已跑通','连续对话、六维复盘、画像、经验与纪要导入。'),(3.8,'浏览器与导出已验收','真实 Chromium、四主题、HTML / PDF 导出。'),(5.03,'支持本地启动与多服务商','保留 OpenAI 兼容 API 和已有配置能力。')]:
 text(s,4.25,y,5.05,.43,title,19,INK,True);text(s,4.25,y+.51,5.05,.62,body,15,MUTED)
text(s,.74,6.45,8.5,.4,'试点待采集：真实提取质量、沟通改善幅度、准备时间与使用反馈。',14,RED,True)
note(s,'可运行的原型，已经具备完整训练闭环。','已实现：连续对话、六维复盘、双侧画像、经验库、会议纪要导入。\n已验收：68项后端测试、真实Chromium流程、四主题、HTML/PDF导出。\n支持本地启动和OpenAI兼容服务商。\n待试点采集：真实提取质量、沟通改善幅度、准备时间与反馈。','目前已经完成可本地启动的原型和主要功能闭环，68项后端测试以及浏览器流程验证已经通过。这里需要把证据边界讲清楚：这些验证说明流程和协议可运行，没有证明沟通能力提升了某个百分比。真实提取质量、节省时间和应用效果，需要下一步通过脱敏试点收集。')

s=slide('第三部分  亮点','把操作门槛降到一句自然语言','想改什么，直接说。')
box(s,.65,2.42,8.7,1.18,RED,RED);text(s,.9,2.64,8.2,.72,'“朱总更重视风险边界，补到画像里。”\n“把追问强度调为深入。”',21,WHITE,True)
picture(s,'free-input.png',.65,3.92,8.7,2.75)
text(s,.7,6.76,8.6,.22,'自然语言可新增对象、补充画像与语录、调整强度、收录经验；原表单保留。',10,MUTED)
note(s,'想改什么，直接说。','朱总更重视风险边界，补到画像里。\n把追问强度调为深入。\n自然语言可新增对象、补充画像和语录、调整追问强度、收录经验。原表单保留。','用户不用每次都把所有字段填一遍。可以直接说朱总今天说了什么、自己观察到什么，或者希望把追问强度调高一点。系统整理后列出保存结果；不明确的对象会继续询问。原来的表单保留，适合做精细修改。')

s=slide('第三部分  亮点','让资料、练习和反思互相连接','越用，越贴近自己的工作场景。')
card(s,.65,2.48,4.12,1.48,'真实工作资料','纪要、语录、项目背景\n成为有来源的训练输入。','01')
card(s,5.22,2.48,4.12,1.48,'有目标的连续对话','围绕交付、风险和决策\n根据上下文合理追问。','02')
card(s,5.22,4.5,4.12,1.48,'基于原话的复盘','回看每轮表达的依据\n保留评分和改进示范。','03')
card(s,.65,4.5,4.12,1.48,'可积累的画像与经验','总结个人表达特征\n为后续练习提供参考。','04')
text(s,4.78,2.9,.45,.4,'→',23,RED,True,PP_ALIGN.CENTER);text(s,7.05,4.03,.4,.38,'↓',23,RED,True,PP_ALIGN.CENTER);text(s,4.78,4.95,.45,.4,'←',23,RED,True,PP_ALIGN.CENTER);text(s,2.42,4.03,.4,.38,'↑',23,RED,True,PP_ALIGN.CENTER)
text(s,.75,6.41,8.5,.37,'旧训练保留快照，新的观察与经验用于下一次练习。',16,RED,True,PP_ALIGN.CENTER)
note(s,'越用，越贴近自己的工作场景。','工作资料 → 连续对话 → 原话复盘 → 画像与经验 → 下一次练习。\n旧训练保留快照，新观察和新经验用于后续练习。','这项应用的积累价值来自这个循环。工作资料让练习更贴近现实，连续对话暴露表达中的空缺，复盘把问题变成可执行的改法，再沉淀为画像和经验。历史训练保留当时的快照，避免后来的资料更新改写过去的评分依据。')

s=slide('第三部分  亮点','现场演示建议','从一句“差不多”，走到明确的下一步。')
for y,num,title,body in [(2.5,'01','选朱总，进入项目汇报','带入一份脱敏背景，明确本轮要达成的决定。'),(3.52,'02','先用糟糕回答试一次','输入“差不多、一直加班”，观察后续追问。'),(4.54,'03','结束并复盘，找到改法','查看六维依据、逐轮点评和改进示范。'),(5.56,'04','换一种回答，再练一次','补上判断、事实、边界和请求，继续迭代。')]:
 box(s,.65,y,8.7,.86);text(s,.85,y+.14,.65,.48,num,24,RED,True);text(s,1.65,y+.12,7.35,.31,title,18,INK,True);text(s,1.65,y+.48,7.35,.27,body,13,MUTED)
note(s,'现场演示：从差不多走到明确下一步。','1. 选朱总，带入脱敏背景。\n2. 用糟糕回答试一次，观察追问。\n3. 结束并复盘，查看依据和改进示范。\n4. 换一种更清楚的回答，再练一次。','现场可以这样演示：先选朱总和项目汇报，输入那段差不多、一直加班的回答，看看对方会追问什么；然后结束并复盘，找到一个最需要改的点；最后换成更明确的回答再练。另可演示导入纪要和自由输入。建议提前准备脱敏样例及一份已保存的复盘，模型响应较慢时仍能讲清流程；所有示例数据明确标为虚构。')

# Put the supplied closing last and refresh only its text.
for sh in closing.shapes:
 if sh.has_text_frame and '感谢观看' in sh.text:set_shape(sh,'让每一次表达，\n都推动事情向前。',30,INK,True)
 elif sh.has_text_frame:set_shape(sh,'AI职场沟通训练师  |  感谢观看',17,RED,True)
last=prs.slides._sldIdLst[1];prs.slides._sldIdLst.remove(last);prs.slides._sldIdLst.append(last)
note(closing,'让每一次表达，都推动事情向前。','AI职场沟通训练师。\n把下一次高压沟通，提前练一遍。\n感谢观看。','我们希望让重要沟通多一次准备，让每一次表达更能推动事情向前。把下一次高压沟通，提前练一遍。谢谢大家。')
prs.core_properties.title='AI职场沟通训练师｜AI赋能·智创未来'
prs.core_properties.subject='项目成果展示；界面与案例说明；含逐页讲述稿'
prs.core_properties.author='项目展示材料'
prs.core_properties.keywords='AI,职场沟通,中国中车,会议纪要,六维复盘'
prs.save(OUT)
md=['# AI职场沟通训练师｜项目成果展示','', '建议讲述 6–8 分钟，另留现场演示时间。使用用户提供的中国中车模板，保持 4:3 版式。案例和对话为虚构演示，不作为实际项目结论或实测模型效果。','']
for i,item in enumerate(content,1):md.extend([f'## {i:02d}｜{item["title"]}','','**页面内容**','',item['body'],'','**讲述稿**','',item['speech'],''])
(ROOT/'项目展示内容与讲述稿.md').write_text('\n'.join(md),encoding='utf-8')
import json
(ROOT/'slide-content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Built',OUT.name,'slides:',len(prs.slides))
