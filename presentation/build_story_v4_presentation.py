"""Revise the user's uploaded v3; retain untouched pages and original cover edits."""
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
ASSETS=ROOT/'assets-v4'
SOURCE=ROOT/'source-story-v3-user.pptx'
prs=Presentation(SOURCE)
original=list(prs.slides)
rows=json.loads((ROOT/'story-v3-content.json').read_text())
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
 for p in new.shapes.title.text_frame.paragraphs:
  for r in p.runs:r.font.name=FONT;r.font.size=Pt(24);r.font.bold=True;r.font.color.rgb=RGBColor.from_string(INK)
 sid=prs.slides._sldIdLst[-1];prs.slides._sldIdLst.remove(sid)
 target=next(i for i,s in enumerate(prs.slides) if s==sl)
 prs.slides._sldIdLst.insert(target+1,sid)
 return new

# 1. Bring the omitted score header into the main narrative, at full width.
s=insert_after(original[7]);title='结束训练，先看到本轮总分。';prepare(s,title)
picture(s,'review-summary.png',.65,2.48,8.7,2.0)
picture(s,'review-focus.png',.65,4.65,8.7,1.04)
text(s,.78,5.98,8.5,.36,'总分为六维平均取整数；下一页再看具体维度。',16,MUTED)
foot(s,f'本轮总分 {review["score"]} / 100：先看结论，再定位最值得练的一点。')
record(s,title,f'本轮六维平均分 {review["score"]} / 100，保留完整评分首屏。','点击结束并复盘后，首先看到本轮总分。这里是68分，来自六个维度的平均取整；下方同时给出较高得分项和下一轮重点。分数用于定位本例的表达问题，再回到原话找依据。','再把总分拆开，看六个维度分别反映什么。','导航选中沟通训练；依次指68分、六维平均分、下一轮优先练习。')

# 2. Actual radar screenshot plus an editable, large numeric table from the same record.
s=original[8];title='六个维度，每一项都有明确分数。';prepare(s,title)
picture(s,'review-radar-chart.png',.63,2.5,4.35,3.91)
text(s,5.32,2.48,4.0,.32,'本轮各维评分 / 100',13,RED,True)
for i,d in enumerate(review['dims']):
 y=2.99+i*.52
 text(s,5.32,y,2.83,.4,d['name'],18)
 text(s,8.30,y-.04,.96,.60,str(d['score']),25,RED,True)
foot(s,'本例优先看“证据具体 64”与“诉求对齐 58”，再回到原话练。')
record(s,title,'六维分数与同轮总分使用同一份复盘记录，清楚展示每项数值。','左边是产品实际雷达截图，右边把同一份复盘记录的六项分数放大。证据具体64分、诉求对齐58分，是本例最值得继续练的两项。讲述时不必逐项念完，接下来直接看原回答怎样改。','定位到缺口之后，最关键的是给出可以练的下一句话。','先指实际雷达，再指64和58；分数为明确标注的演示样例，不作真实效果承诺。')

# 3. Give accumulated portrait observations, next steps and sources readable space.
s=original[11];title='三场训练，18 次回应，画像开始有了内容。';prepare(s,title,'portrait')
picture(s,'portrait-summary.png',.65,2.4,8.7,1.78)
text(s,.72,4.35,8.5,.35,'反复出现的沟通特征',14,RED,True)
picture(s,'portrait-traits-first.png',.65,4.83,8.7,1.48)
foot(s,'项目汇报、资源协调、异常说明三场练习，形成有原话依据的观察。')
record(s,title,'三场六轮演示训练，累计18次用户回应，画像不再只有少量空泛内容。','除了刚才的交付汇报，我又完成了资源协调和异常说明两场练习，每场六轮，总共18次回应。现在画像有了持续积累的摘要，也能看到反复出现的习惯：倾向先推进，追问后再补齐依据。这里仍只反映这些练习。','除了描述习惯，画像还要告诉用户保留什么、下一步练什么。','导航选中我的沟通画像；指3场训练、18条回应，再指沟通特征。',35)

t=insert_after(s);title='保留已有优势，再给下一轮一个具体练法。';prepare(t,title,'portrait')
text(t,.72,2.37,8.5,.35,'已有优势',14,RED,True)
picture(t,'portrait-strengths-first.png',.65,2.87,8.7,1.40)
text(t,.72,4.43,8.5,.35,'提升方向与练习措施',14,RED,True)
picture(t,'portrait-directions-first.png',.65,4.88,8.7,1.47)
foot(t,'保留主动承担、明确反馈的优势；下一轮把决策请求说短、说清。')
record(t,title,'画像同时给出已有优势、提升方向与可执行的练习措施。','上面是已有优势：愿意接住责任，也能给出反馈时间。下面是下一步的练法：把请求单独说清楚，明确请对方在什么时候确认哪个选择。用户可以把这一条带回同场景再练。','这些观察不是凭空贴标签，下面看看它们引用了哪些原话。','先指已有优势，再指提升方向里的练习措施。')

t=insert_after(t);title='每一条观察，都能回到说过的原话。';prepare(t,title,'portrait')
text(t,.72,2.37,8.5,.35,'同一条观察，引用三场训练中的实际演示回应',14,RED,True)
for i in range(3):picture(t,f'portrait-source-{i+1}.png',.65,2.93+i*1.11,8.7,1.00)
foot(t,'每条证据保留“查看来源训练”入口，回看当时的完整上下文。')
record(t,title,'沟通画像引用三场训练的实际演示原话，来源入口已经点击核对。','这里展开同一观察的原话依据：有异常说明里的事实与假设区分，也有资源协调和交付汇报里的判断依据。每条都有来源训练按钮，能返回完整上下文。画像因此可以被核对，也方便用户判断建议是否适用于下一次。','刚才解决了怎样练、怎样积累；真实对象和项目背景又从哪里来？','指三条原话与对应的来源训练按钮；强调原话来自已完成的三场演示训练。')

# Refresh selected existing screenshots, retaining the user's other pages verbatim.
old_hashes={hashlib.sha256(p.read_bytes()).hexdigest():p.name for p in (ROOT/'assets-v3').glob('*.png')}
for index,names in [(9,{'round-review.png'}),(10,{'next-actions.png'}),(18,{'history.png'})]:
 sl=original[index]
 for sh in list(sl.shapes):
  if sh.shape_type!=MSO_SHAPE_TYPE.PICTURE:continue
  name=old_hashes.get(hashlib.sha256(sh.image.blob).hexdigest())
  if name not in names:continue
  x,y,w,h=[v/914400 for v in (sh.left,sh.top,sh.width,sh.height)]
  if name=='history.png':x,y,w,h=.65,2.78,8.7,3.05
  sl.shapes._spTree.remove(sh._element);picture(sl,name,x,y,w,h)

# Speaker notes and page numbers follow the new order, including hidden appendices.
content=[]
for i,sl in enumerate(prs.slides,1):
 row=dict(row_by_part[sl.part.partname]);row['page']=i
 if i==12:row['transition']='接下来，多完成几场练习，看看个人画像怎样积累。'
 if sl==original[22]:row['transition']='欢迎交流；备用页24、25可按需打开。'
 sl.notes_slide.notes_text_frame.text=f'【建议停留】{row["seconds"]}秒\n【本页一句话】{row["body"]}\n【看图指向】{row["point"] or "按页面顺序讲述"}\n【讲述稿】\n{row["speech"]}\n【转场】\n{row["transition"]}'
 for sh in list(sl.shapes):
  if sh.has_text_frame and sh.text.strip().isdigit() and sh.top>Inches(7):sl.shapes._spTree.remove(sh._element)
 if i not in [1,len(prs.slides)]:text(sl,.54,7.1,.45,.23,str(i).zfill(2),9,MUTED)
 content.append(row)

prs.core_properties.title='AI职场沟通训练师｜第四版 · 多轮画像与清晰评分'
prs.core_properties.subject='基于用户上传第三版修订，补充三场18次回应画像、独立总分与六维数值'
prs.save(ROOT/'AI-workplace-coach-story-v4.pptx')
(ROOT/'story-v4-content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
duration=sum(c['seconds'] for c in content if not c['appendix'])
md=['# AI职场沟通训练师｜第四版讲述稿','','基于用户上传的第三版修订，保留用户调整的封面。简介先背景、需求、方案，最后一页引入产品截图。',
 '', '26页，24页主讲；第24、25页为默认隐藏备用页，放映1–23 → 26。PDF包含全部页面。主讲约'+str(round(duration/60,1))+'分钟，另留操作与提问。',
 '', '第9页：总分68 / 100。第10页：六维分数72、64、58、74、68、72；总分按均值取整。第13–15页：三场训练、18次回应后的画像、优势与方向、三场原话来源。',
 '', '案例、评分与分析为隔离环境中的本机演示数据，经真实页面操作和原有校验生成，不代表真实模型或业务效果。','']
for c in content:
 md.extend([f'## {c["page"]:02d}｜{c["title"]}'+('（隐藏备用）' if c['appendix'] else ''),'',f'**本页重点**：{c["body"]}','',f'**建议停留**：{c["seconds"]}秒','',f'**看图指向**：{c["point"] or "按页面顺序讲述"}','','**讲述稿**','',c['speech'],'','**转场**','',c['transition'],''])
(ROOT/'项目展示内容与讲述稿-第四版.md').write_text('\n'.join(md))
print('Built v4:',len(prs.slides),'pages;',duration,'main seconds; score',review['score'],'portrait',portrait['sessionCount'],portrait['sampleCount'])
