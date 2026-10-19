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
OUT=ROOT/'AI-workplace-coach-story-v3.pptx'
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
 path=ROOT/'assets-v3'/name
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
 elif sh.name=='文本占位符 3':set_shape(sh,'“AI赋能·智创未来”AI应用成果发布\n成果展示 · 第三版 · 案例主线',14,MUTED)
 elif sh.name=='文本占位符 9':set_shape(sh,'项目汇报 / 技术评审 / 客户沟通 / 国际协作',11,MUTED)

MAIN='第一部分  项目简介';CASE='第二部分  应用成效';VALUE='第三部分  亮点'
CAPTION='界面实拍｜案例、评分与分析为本机演示数据，非真实模型或业务效果实测'

def record(sl,title,body,speech,transition,seconds=25,point='',appendix=False):
 number=len(content)+1
 sl.notes_slide.notes_text_frame.text=f'【建议停留】{seconds}秒\n【本页一句话】{body}\n【看图指向】{point or "按页面顺序讲述"}\n【讲述稿】\n{speech}\n【转场】\n{transition}'
 if appendix:sl._element.set('show','0')
 content.append({'page':number,'title':title,'body':body,'speech':speech,'transition':transition,'seconds':seconds,'point':point,'appendix':appendix})

def slide(part,kicker,title):
 sl=prs.slides.add_slide(prs.slide_layouts[2]);set_shape(sl.shapes.title,part,24,INK,True)
 label(sl,.52,1.06,8.9,kicker);text(sl,.52,1.48,8.95,.75,title,27,INK,True)
 text(sl,.54,7.1,.45,.23,str(len(content)+1).zfill(2),9,MUTED)
 return sl

def foot(sl,caption,source=True):
 text(sl,.62,6.53,8.85,.35,caption,13,RED,True,PP_ALIGN.CENTER)
 if source:text(sl,.62,6.94,8.85,.2,CAPTION,9,MUTED)

def shot(part,kicker,title,image,caption,speech,transition,seconds=25,point='',points=None,appendix=False):
 s=slide(part,kicker,title)
 if points:
  picture(s,image,.58,2.37,6.18,4.13)
  for i,(head,body) in enumerate(points):
   y=2.56+i*1.22;text(s,7.03,y,2.3,.4,head,17,RED,True);text(s,7.03,y+.47,2.3,.68,body,13,MUTED)
 else:picture(s,image,.55,2.32,8.9,4.12)
 foot(s,caption)
 record(s,title,caption,speech,transition,seconds,point,appendix)
 return s

record(cover,'AI职场沟通训练师','把下一次高压沟通，提前练一遍。','大家好，今天介绍的是 AI职场沟通训练师。先从一个熟悉的工作问题说起：技术材料准备了很多，到了关键的几句汇报，怎样让对方听清判断、看见依据，并能做出决定？','先看这个问题在日常工作中怎样出现。',15)

# 02–04 establish context, need and project positioning. No app screenshots here.
s=slide(MAIN,'背景 / 技术工作需要转化为共同决定','工作推进，常常取决于关键的几句沟通。')
for y,num,title,body in [(2.5,'01','项目汇报','现状是什么？哪些风险需要决策？'),(3.67,'02','技术评审','结论依据什么？适用边界在哪里？'),(4.84,'03','客户协调','能承诺什么？需要对方配合什么？')]:
 box(s,.65,y,8.7,.99);text(s,.87,y+.18,.6,.48,num,26,RED,True);text(s,1.67,y+.13,2.3,.4,title,19,INK,True);text(s,4.0,y+.26,5.05,.4,body,17)
foot(s,'技术事实讲清楚，才能让协作进入下一步。',False)
record(s,'工作推进，常常取决于关键的几句沟通。','项目汇报、技术评审、客户协调，都需要把事实转化为可执行的共同决定。','我们的工作里有很多技术事实，但沟通最终还要回答几个问题：现在是什么状态，结论靠什么支撑，需要谁做什么决定。项目汇报、技术评审和客户协调都离不开这个过程。即使材料充分，到了临场追问，也可能遗漏关键的一环。','把这个背景缩小到一次交付前的周会。',25,point='依次指项目汇报、技术评审、客户协调；不展开三段不同故事。')

s=slide(MAIN,'需求 / 一次交付前的周会','材料准备了很多，关键追问仍可能答不清。')
box(s,.65,2.48,8.7,1.32,RED,RED);text(s,.93,2.65,8.15,.99,'朱总：“周五能不能交付？\n今天需要我决定什么？”',25,WHITE,True)
label(s,.8,3.94,2.0,'熟悉的回答');text(s,.8,4.35,8.35,.56,'“基本都差不多了，大家最近一直在加班……”',22)
for x,title,body in [(.8,'判断','能交付到什么范围？'),(3.82,'依据','哪些验证已经关闭？'),(6.84,'请求','需要对方决定什么？')]:
 text(s,x,5.35,2.5,.4,title,19,RED,True);text(s,x,5.92,2.5,.55,body,15)
text(s,.65,6.88,8.7,.22,'本场景为虚构演示，用于说明训练目标，不是实际项目结论。',9,MUTED)
record(s,'材料准备了很多，关键追问仍可能答不清。','围绕一个交付问题：补齐判断、验证依据和具体决策请求。','假设周会前，朱总问：周五能不能交付，今天需要我决定什么？我们可能先说大家一直在加班、项目差不多了。请停一秒想一想：这句话之后，对方能做决定吗？我们要练的就是下面三件事——交付判断、验证依据和决策请求。','这三个缺口，就是项目要解决的具体问题。',30,point='先读红色提问，再读回答；停顿一秒，最后落到判断、依据、请求。')

s=slide(MAIN,'总体介绍 / 面向工作场景的 AI 沟通练习','给重要沟通，增加一轮可反复练习的准备。')
for x,num,title,body in [(.65,'01','会前练','选对象与目标\n在连续追问中练表达'),(3.65,'02','练后复盘','回看原话与依据\n对照示范调整说法'),(6.65,'03','持续积累','留住纪要与语录\n沉淀画像、背景和经验')]:card(s,x,2.7,2.7,2.17,title,body,num)
box(s,.65,5.27,8.7,.82,WHITE,RED);text(s,.9,5.49,8.2,.42,'AI 模拟沟通对象  +  六维原话复盘  +  工作资料沉淀',19,RED,True,PP_ALIGN.CENTER)
foot(s,'定位：面向具体工作任务的沟通训练工具。',False)
record(s,'给重要沟通，增加一轮可反复练习的准备。','项目把会前练习、练后复盘和资料积累接成闭环。','项目定位是面向具体工作任务的沟通训练工具。它让用户先练一次：AI根据角色和上下文追问，练后对照原话、依据与示范，再把有价值的观察和工作资料留给下一次。这样每一项功能都有明确去处：支持下一次更有准备的沟通。','有了这个定位，再看产品如何承接刚才那个问题。',25,point='只讲会前练、练后复盘、持续积累三步；接口和设置不在这里展开。')

# Last introduction slide is the only introduction page with a product screenshot.
shot(MAIN,'引入项目 / 从交付前的一次汇报看完整闭环','接下来，只看一件事：怎样向朱总汇报交付。','workspace-overview.png','带着同一个交付问题，看练习、复盘与资料积累如何接起来。','这是已经可以本地启动的项目界面。今天不逐个讲菜单，我们只沿着刚才的任务走一遍：向朱总说明验证状态，明确交付边界，并提出台架优先级的决策请求。画面里的功能，会随着这个任务依次出现。','第一步，先把这轮练习要达成什么说清楚。',15,point='只指训练入口；此时不逐项解释顶部和底部菜单。')

shot(CASE,'案例 · 练前 / 明确这次要推动什么','先把目标定清楚：说边界，提请求。','training-setup.png','本轮目标：说明验证边界，提出台架优先级的决策请求。','这里选朱总作为沟通对象，把本轮目标写具体：说明验证边界，并提出台架优先级的决策请求。背景可以继续编辑，追问强度也可以调整。演示时只指对象和目标两处，不逐项解释表单。','目标定好了，我们先用那句常见的回答试一次。',20,point='沟通对象“朱总”；本次训练目标。')
shot(CASE,'案例 · 练中 / 模糊表达怎样被继续追问','一句“差不多”，把问题带到了验证依据上。','conversation.png','追问落在“哪些验证已关闭”和“具体交付什么范围”。','先看中间这句回应：基本都差不多，大家最近一直在加班。朱总紧接着追问：哪些验证已经关闭，周五具体交付什么范围？这一步把讨论推进到了可核实的条件。练习者也就看见，下一句需要补的是什么。','如果一时没读懂对方为什么这样追问，可以展开这一句。',35,point='按开场、用户回答、后续追问的顺序读；重点停在后续追问。')
shot(CASE,'案例 · 理解 / 把追问读回工作任务','对方在追问什么，展开一句就能分层看。','three-level.png','把“问了什么、关心什么、依据什么”分开理解。','这里把刚才的一句追问展开。表面是在问验证状态，核心是希望有依据地判断交付，进一步还涉及责任分工和后续同步。讲述时只抓住这条工作线索，不需要把三层文字逐字念完；界面也明确提示，这是一种模拟推断。','读懂了这个问题，练后就能更具体地找自己的表达缺口。',20,point='依次指出表面问题、核心关切、判断依据。')
shot(CASE,'案例 · 复盘 / 先定位最值得改的一点','先看两个维度：证据够不够，请求清不清。','review-radar.png','本例只聚焦“证据具体”和“诉求对齐”，其余维度可按需展开。','结束训练后进入六维复盘。现场不用把六项都解释一遍，这一例只看证据具体和诉求对齐：前者提醒补齐验证状态，后者提醒把协调请求说成一个能被决定的问题。接下来回到刚才那句原话，看究竟怎么改。','定位到缺口之后，最关键的是给出可以练的下一句话。',25,point='右侧“证据具体”和“诉求对齐”两行；不围绕演示分数作效果承诺。')
shot(CASE,'案例 · 改法 / 原话与示范直接对照','把“差不多”，改成有边界、有安排的回应。','round-review.png','已知的说事实，未知的留待核实，请求落到具体决定。','左边保留原回答，右边给出改进示范。变化落在三个地方：先说明当前能承诺到哪里，再说明要核实什么、何时反馈，最后提出台架优先级请求。示范中的未知项保留占位，使用者需要补入核实过的信息。','这一轮不用同时改好所有问题，先挑一条再练。',35,point='先读左边原回答，再指右边的边界、核查安排、决策请求。')

s=slide(CASE,'案例 · 再练 / 把反馈变成下一次行动','下一轮只练一件事：把请求说到能被决定。')
label(s,.7,2.36,8.5,'从复盘中挑一条最优先的建议');picture(s,'next-actions.png',.65,2.79,8.7,2.65)
label(s,.7,5.56,8.5,'同场景再练，继续用这个任务练习');picture(s,'export-actions.png',.65,6.0,8.7,.43)
foot(s,'用户选定练习重点后，再回到同一个场景开口。')
record(s,'下一轮只练一件事：把请求说到能被决定。','从下一轮建议中选择一项，再用同场景练习验证自己的新说法。','这一轮先挑一件事：用一句话讲清请朱总决定什么、最晚什么时候决定。用户可以点击同场景再练，把目标手动改成这条要求，继续开口。至此，我们已经走完目标、对话、复盘、改法和再练这一轮闭环。','这轮原话还会留下来，为认识自己的表达习惯提供线索。',20,point='先指具体建议，再指“同场景再练”；不要承诺系统自动改写训练目标。')

s=slide(CASE,'案例 · 积累 / 让本轮原话留下可回看的线索','从这一轮，开始积累有依据的表达观察。')
picture(s,'portrait-summary.png',.65,2.4,8.7,1.23);picture(s,'portrait-evidence.png',.65,3.8,8.7,2.58);foot(s,'少量样本标为初步观察，每项都能回到来源原话。')
record(s,'从这一轮，开始积累有依据的表达观察。','个人画像保留原话依据与来源训练，初步观察不作稳定人格结论。','这一轮练习会进入个人沟通画像。上面是初步总结，下面可以回看支撑它的原话。样本还少，所以它提供的是观察线索和练习方向，不能据此给自己定性。到这里，这次练习的内容既能当场改，也有后续积累。','刚才解决了怎样练。再往前一步：真实的朱总和项目背景，从哪里来？',20,point='“初步画像”提示；原话证据与来源训练。')

shot(VALUE,'同一案例 · 真实资料 / 让下一次练习更贴近工作','下次准备背景，可以直接从周会纪要开始。','meeting-input.png','把已经记录的人、事和决定，整理成可复用的训练资料。','刚才的练习能不能贴近工作，还取决于输入资料。朱总说过什么、项目验证到哪一步，这些往往已经写在周会纪要里。用户可以导入文件或粘贴正文，先检查、脱敏，再请求提取，减少重复整理背景的负担。','有了原始资料，下一步先核对提取结果是否归对了人和事。',20,point='纪要正文中的朱总发言、A项目状态与行动项；文件格式带过即可。')
shot(VALUE,'同一案例 · 核对 / 更新资料之前先看依据','先核对：这是谁说的，依据写在哪里？','meeting-preview.png','每项保留原文依据，人物归属可调整，勾选后再保存。','以这条关于朱总的观察为例，页面保留了对应的原文依据，人物归属可以重新选择，条目也可以取消勾选。用户核对后才保存。接下来我们只看这份纪要怎样留下三类有用的东西：人的关注点、项目背景和可复用方法。','先看关于朱总的资料，怎样变得更有依据。',20,point='“归入哪个对象”选择框；“查看原文依据”；条目勾选。')
shot(VALUE,'同一案例 · 留下人的线索 / 对象语录与画像','关于朱总的新增观察，都能回到记录的原话。','quote-analysis.png','原话、特征推测和模拟表达分别呈现。','纪要和日常记录里的语句，可以继续进入对象语录。对朱总的沟通偏好，系统给出有引用依据的谨慎推测；可能的模拟表达则另行标注。这样下一次练习可以参考这些资料，原话和推测也不会混在一起。','人的线索留下来了，再看这次项目状态怎样接到下一次练习。',15,point='特征推测及其原话依据；“可能的表达·AI模拟”。',points=[('记住说过的话','语录是参考资料。'),('谨慎总结偏好','推测必须有原话依据。'),('分清模拟表达','模拟台词另行标注。')])

s=slide(VALUE,'同一案例 · 留下事情的上下文 / 项目背景','验证状态和行动项，下次可以直接接着用。')
label(s,.7,2.35,8.5,'纪要中保存的 A 项目背景');picture(s,'project-background.png',.65,2.79,8.7,1.18)
label(s,.7,4.03,8.5,'训练页选择项目，并编辑本次背景');picture(s,'project-context.png',.65,4.44,8.7,1.91);foot(s,'新训练引用当前背景，旧训练保留当时的快照。')
record(s,'验证状态和行动项，下次可以直接接着用。','项目背景可以继续编辑后引用；资料更新不改写旧训练。','上图保留这次项目状态和行动项，下图是在训练页选择并引用它。用户还可以继续编辑本轮背景。下一次准备交付汇报，就有一个可核对、可更新的起点；旧训练仍保留当时的资料，避免前后混淆。','这次讨论里值得复用的方法，也可以单独留下。',15,point='保存的项目背景；训练页项目下拉框与背景正文。')
shot(VALUE,'同一案例 · 留下方法 / 沟通经验库','这次学到的“先讲边界”，下次还能找到。','experience-source.png','经验保留适用内容和来源依据，可进入经验库检索与复用。','这一条经验来自刚才的演示纪要：先明确验证边界，再承诺交付。它带着来源原文，便于判断适用场景，也能进入经验库检索。至此，一份资料留下了人的线索、事情的上下文和可复用的方法。','如果下一次只有一句零散的新观察，也不用重新填完所有表格。',20,point='经验正文；纪要原文依据；来源纪要入口。',points=[('人的线索','对象关注点与语录。'),('事的上下文','项目状态与行动项。'),('可复用的方法','经验带着来源保存。')])

s=slide(VALUE,'同一案例 · 持续补充 / 自由输入','零散的新观察，也能用一句话补进来。')
label(s,.7,2.33,8.5,'一句自然语言，补充今天的新观察');picture(s,'free-input-command.png',.65,2.77,8.7,1.18)
label(s,.7,4.05,8.5,'逐项列出保存后的办理结果');picture(s,'free-saved-result.png',.65,4.49,8.7,1.81);foot(s,'补充画像、追加语录、调整下轮强度，都有办理结果可核对。')
record(s,'零散的新观察，也能用一句话补进来。','自然语言补充对象观察、原话和训练强度，原表单继续保留。','比如会后又听到朱总一句新说法，用户可以直接输入：补到画像和语录，并把下一轮追问调为深入。界面会逐项列出办理结果，方便核对。这种零散信息的积累，也能沿着刚才的人、事和方法继续往下接。','资料能更新，练过的记录也需要能回看、能带走。',20,point='上方命令中的三项需求；下方对应的三条保存结果。')

s=slide(VALUE,'让练习留得住 / 历史与导出','今天练过什么，之后随时能回来看。')
label(s,.7,2.34,8.5,'从训练记录回到同一次练习');picture(s,'history.png',.65,2.78,8.7,2.75)
label(s,.7,5.54,8.5,'保留原话与复盘，也可以导出分享');picture(s,'export-actions.png',.65,6.02,8.7,.44)
foot(s,'历史可回看，支持 HTML、完整 JSON 和打印 / PDF。')
record(s,'今天练过什么，之后随时能回来看。','训练原话、复盘和来源记录保留，结果可以回看或导出。','演示的这轮对话、复盘和原话证据都保存在记录里，可以再次打开，也能导出HTML、完整记录或PDF。讲述时把它当作这一轮案例的留档结果即可，具体导出格式可以在提问环节再展开。','最后回到项目本身：目前交付了什么，下一步该验证什么？',10,point='同一次训练记录；查看记录与导出按钮，不逐个讲按钮。')

s=slide(VALUE,'成果与下一步 / 把交付和验证分开说明','训练与资料闭环已打通，下一步验证真实效果。')
box(s,.65,2.48,4.22,3.58,PALE,LINE);box(s,5.12,2.48,4.22,3.58,WHITE,RED)
label(s,.91,2.75,3.7,'已经交付');text(s,.91,3.23,3.68,2.42,'可本地启动的训练与复盘\n对象、背景、经验的整理路径\n有来源的画像与历史记录\n68 项后端测试与浏览器验收',18)
label(s,5.38,2.75,3.7,'下一步试点验证');text(s,5.38,3.23,3.68,2.42,'使用脱敏的真实工作场景\n核对人物归属与提取质量\n观察请求与边界能否说清\n采集准备时间和使用反馈',18)
text(s,.72,6.39,8.6,.55,'当前测试验证流程；真实模型质量与业务改善仍需试点。',14,RED,True,PP_ALIGN.CENTER)
record(s,'训练与资料闭环已打通，下一步验证真实效果。','已经交付可运行流程；真实提取质量、表达改善和准备时间需要试点采集。','回顾刚才的案例，项目已经把练前准备、连续对话、逐轮复盘，以及资料回用接成闭环。目前68项后端与浏览器流程验收，验证的是协议和流程。下一步用脱敏真实场景试点，核对模型理解与归属，观察请求和边界是否更清楚，并收集准备时间与反馈。','让重要沟通多一次准备，就是这个项目希望带来的价值。',25,point='先总结已经交付的三条闭环，再用一句话说明试点；不编造改善比例。')

# Keep product breadth available for questions without interrupting the main story.
shot('备用页  对象管理','提问时按需打开 / 默认隐藏','对象可以按工作角色维护，也能新增、编辑和删除。','objects-with-tabs.png','朱总、严工及其他对象保留独立的目标、关注点和模拟边界。','如果有人关心对象怎样维护，可以用这一页补充：卡片可编辑，语录可独立分析，新增与删除也有入口。它属于补充说明，不占用主讲时间。','回答后回到总结或结束页。',0,point='新增、编辑、删除与语录分析入口。',appendix=True)
s=slide('备用页  四套主题','提问时按需打开 / 默认隐藏','公司展示使用企业红，日常也可以换成自己的颜色。')
for x,y,name,title in [(.63,2.34,'corporate','企业红 · 默认'),(5.14,2.34,'forest','森林绿'),(.63,4.48,'ocean','海洋蓝'),(5.14,4.48,'violet','鸢尾紫')]:
 picture(s,'theme-'+name+'.png',x,y,4.22,1.76);label(s,x,y+1.77,4.22,title)
text(s,.62,6.73,8.85,.25,'四套实际主题，切换记住本机选择。',12,RED,True,PP_ALIGN.CENTER)
text(s,.62,7.0,8.85,.15,'实际产品主题截图；资料为本机演示数据。',8,MUTED)
record(s,'公司展示使用企业红，日常也可以换成自己的颜色。','企业红为默认主题，同时保留森林绿、海洋蓝和鸢尾紫。','如果有人关心视觉适配，再补充这一页。默认企业红迎合公司展示需求，其余三套主题可按本机喜好切换。它作为备用内容，避免在主线结束时突然转入颜色介绍。','回到结束页。',0,point='四套配色对比；无需阅读截图内正文。',appendix=True)

for sh in closing.shapes:
 if sh.has_text_frame and '感谢观看' in sh.text:set_shape(sh,'让下一次关键沟通，\n多一份准备。',30,INK,True)
 elif sh.has_text_frame:set_shape(sh,'AI职场沟通训练师  |  感谢观看',17,RED,True)
last=prs.slides._sldIdLst[1];prs.slides._sldIdLst.remove(last);prs.slides._sldIdLst.append(last)
record(closing,'让下一次关键沟通，多一份准备。','把下一次高压沟通，提前练一遍。','我们从一句“周五能不能交付”出发，走完了练习、复盘、再练和资料积累。希望用户在关键沟通发生前，多一次有目标的准备。把下一次高压沟通，提前练一遍。谢谢大家。','可进入提问；备用页21、22可按需打开。',15)

# Capture navigation as real UI, not a drawn menu. Main overviews already contain it;
# detail pages pair a native tab strip with the enlarged continuous-region screenshot.
NAV_CONTEXT={6:'practice',7:'practice',8:'practice',9:'practice',10:'practice',11:'practice',12:'portrait',13:'practice',14:'practice',15:'objects',16:'practice',17:'experiences',18:'practice',19:'history'}
TAB_NAMES={'practice':'沟通训练','portrait':'我的沟通画像','objects':'对象画像','experiences':'沟通经验库','history':'训练记录'}
for page,tab in NAV_CONTEXT.items():
 sl=prs.slides[page-1]
 for sh in sl.shapes:
  if sh.has_text_frame and abs(sh.top/Inches(1)-1.06)<.02:sh.text_frame.clear()
  if sh.has_text_frame and abs(sh.top/Inches(1)-1.48)<.02:
   sh.top=Inches(1.72);sh.height=Inches(.56)
 picture(sl,'nav-'+tab+'.png',.55,.99,8.9,.6)
 row=content[page-1]
 row['point']='导航选中“'+TAB_NAMES[tab]+'”；'+row['point']
 if page in (13,14,16,18):row['point']+='。此功能为页面下方常驻区域，不是独立标签页。'

# Tighten narration to one idea per page; keep transitions separate and actionable.
SPEECH={
1:'大家好，今天介绍 AI职场沟通训练师。技术材料准备了很多，怎样在关键的几句汇报中，让对方听清判断、看见依据，并做出决定？这就是项目的切入点。',
2:'项目汇报、技术评审和客户协调，都要回答三件事：现在是什么状态，结论靠什么支撑，需要谁做什么决定。临场追问中，任何一环遗漏，都可能让讨论停在原地。',
3:'朱总问周五能不能交付，你回答大家一直在加班、项目差不多了。停一秒想想：这句话之后，对方能做决定吗？需要补上的，是交付判断、验证依据和具体请求。',
4:'项目把会前练习、练后复盘和资料积累接成闭环。AI根据角色追问，用户回看原话、依据和示范，再把有价值的观察留给下一次。每项功能都服务于下一次更有准备的沟通。',
5:'这是可本地启动的产品。今天只沿一个任务走：向朱总说明验证状态，明确交付边界，并提出台架优先级请求。功能会随着这个任务依次出现。',
6:'先选朱总，把本轮目标写具体：说明验证边界，并提出台架优先级请求。这里还可以编辑背景和调整强度。演示时只指对象和目标两处。',
7:'先读中间这句回答：基本都差不多，大家最近一直在加班。朱总随后追问哪些验证已经关闭、具体交付什么范围。练习者因此看到，下一句应该补什么。',
8:'展开刚才的追问：表面在问验证状态，核心是判断交付，还涉及责任分工和后续同步。这里抓住工作线索即可；三层解读是模拟推断，不是现实人物的心理事实。',
9:'六维不必逐项念完，本例只看证据具体和诉求对齐：先补足验证状态，再把协调请求说成能被决定的问题。随后回到刚才那句原话，看怎么改。',
10:'左边保留原回答，右边给出示范：先说承诺边界，再说核查安排，最后提出台架优先级请求。未知项保留占位，使用者补入核实过的信息。',
11:'这一轮先挑一件事：讲清请朱总决定什么、何时决定。用户点击同场景再练，手动把目标改成这条要求，就能继续开口。一次练习闭环到这里已经走完。',
12:'这轮原话还会进入个人画像，留下观察和练习方向。样本少时明确标为初步观察，每项都能回到来源原话。它提供线索，不给人定性。',
13:'刚才的练习要贴近工作，需要知道朱总说过什么、验证到了哪一步。这些往往已经在周会纪要里。用户导入资料，先检查和脱敏，再请求提取。',
14:'这一项关于朱总的观察，带着对应原文。人物归属可以改，条目也可以取消勾选，核对后才保存。下面看这份资料怎样留下人、事和方法三个方面的线索。',
15:'记录的语句进入对象语录，支持有引用依据的谨慎推测；可能的模拟表达另行标注。下一次练习能参考这些线索，原话与推测也保持分开。',
16:'项目状态和行动项也能保存，再从训练页选择引用。用户继续编辑本轮背景，旧训练则保留原快照。下次准备同一个项目，就有了可更新的起点。',
17:'这条经验来自刚才的纪要：先明确验证边界，再承诺交付。它带着来源，进入经验库，便于检索和判断适用场景。人的线索、事情的上下文和方法就都留下了。',
18:'会后听到朱总一句新说法，也可以直接输入：补到画像与语录，并把下轮追问调为深入。界面逐项列出办理结果，零散观察也能持续积累。',
19:'这次练习的原话、复盘和依据保存在同一条记录中，随时能回看或导出。具体格式放到提问环节展开，这里把它看作本轮案例的留档结果即可。',
20:'刚才已经走通训练、复盘、再练和资料回用。已有测试验证协议与流程；下一步用脱敏真实场景试点，核对模型理解与归属，观察请求和边界是否更清楚，并采集准备时间和反馈。',
23:'从一句“周五能不能交付”出发，我们走完了练习、复盘和资料积累。希望用户在关键沟通前，多一次有目标的准备。把下一次高压沟通，提前练一遍。谢谢大家。'
}
import math,re
for row,sl in zip(content,prs.slides):
 if row['page'] in SPEECH:row['speech']=SPEECH[row['page']]
 if row['page']==23:row['transition']='欢迎交流。'
 if not row['appendix']:
  estimated=len(re.sub(r'\s','',row['speech']+row['transition']))/220*60
  row['seconds']=max(row['seconds'],int(math.ceil(estimated/5)*5))
 sl.notes_slide.notes_text_frame.text=f'【建议停留】{row["seconds"]}秒\n【本页一句话】{row["body"]}\n【看图指向】{row["point"] or "按页面顺序讲述"}\n【讲述稿】\n{row["speech"]}\n【转场】\n{row["transition"]}'

prs.core_properties.title='AI职场沟通训练师｜背景与案例主线 第三版'
prs.core_properties.subject='简介先背景与总体介绍，后以同一案例串联截图；含逐页讲述稿与转场'
prs.core_properties.author='项目展示材料'
prs.core_properties.keywords='AI,职场沟通,中国中车,案例主线,演讲备注'
prs.save(OUT)
import json
(ROOT/'story-v3-content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
main=[c for c in content if not c['appendix']];duration=sum(c['seconds'] for c in main)
md=['# AI职场沟通训练师｜第三版讲述稿','','主线：背景与需求 → 总体方案 → 同一轮交付汇报练习 → 资料回用 → 当前交付与试点。','','23页，其中21页为主讲，21、22页是默认隐藏的备用页。放映按1–20页后自动跳到23页结束；PDF包含全部23页。建议主讲约9–10分钟，另留现场操作和提问时间。','','简介第2–4页无项目截图，第5页为简介唯一的项目截图。主页面全景保留真实标签页目录，局部放大页配同一分页的真实导航截图，显示当前所属页面。其后围绕向朱总汇报交付状态展开。案例、分数和分析沿用第二版明确标注的本机演示数据，不作为真实模型或业务效果证据。','','## 开场可直接这样讲','',''+content[0]['speech']+' '+content[1]['speech'],'','## 主讲路线','','1–5页：为什么做、要解决什么、项目怎样组织。\n6–12页：同一次训练怎样练、怎样改、怎样留下证据。\n13–19页：同一案例的资料怎样进入并用于后续练习。\n20页：当前交付与真实场景试点。\n23页：结束。21、22页只在提问时按需打开。','','## 讲述提示','','- 每页只讲备注中的一句重点；不读菜单和所有维度。\n- 分数不作提升证明；用原话与改法说明训练价值。\n- 一次只讲同一个交付任务，避免临时切到另一种场景。\n- 截图说明已内嵌PPT备注；转场一句可直接说。\n- 正篇按建议时长总计约'+str(round(duration/60,1))+'分钟，预留停顿或操作时间。','']
for c in content:
 md.extend([f'## {c["page"]:02d}｜{c["title"]}'+('（备用，默认隐藏）' if c['appendix'] else ''),'',f'**本页一句话**：{c["body"]}','',f'**建议停留**：{c["seconds"]}秒', '',f'**看图指向**：{c["point"] or "按页面顺序讲述"}','','**讲述稿**','',c['speech'],'','**转场**','',c['transition'],''])
(ROOT/'项目展示内容与讲述稿-第三版.md').write_text('\n'.join(md),encoding='utf-8')
print('Built',OUT.name,'slides:',len(prs.slides),'main:',len(main),'main seconds:',duration,'appendix:',[c['page'] for c in content if c['appendix']])
