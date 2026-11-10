"""Expression optimization: original user-chosen phrase versus audience-aware request."""
from pathlib import Path
import json
from PIL import Image
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
ROOT=Path(__file__).resolve().parent;A=ROOT/'assets-v13';prs=Presentation(ROOT/'AI-workplace-coach-story-v12.pptx');rows=json.loads((ROOT/'story-v12-content.json').read_text())
def text(sl,x,y,w,h,s,size=18,color='4C4948',bold=False):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 r=tf.paragraphs[0].add_run();r.text=s;r.font.name='Noto Sans CJK SC';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
 ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)
sl=prs.slides[15]
for sh in list(sl.shapes):
 if sh!=sl.shapes.title:sl.shapes._spTree.remove(sh._element)
text(sl,.55,1.02,9,.5,'表达优化：保留具体指代，把抱怨转成诉求。',25,bold=True)
sl.shapes.add_picture(str(A/'nav-expression.png'),Inches(.65),Inches(1.67),width=Inches(8.7))
text(sl,.7,2.29,4.2,.7,'原话输入（情绪化示例）\n“我觉得朱彦霖脑子有问题”',19,'C70019',True)
sl.shapes.add_picture(str(A/'expression-input.png'),Inches(.7),Inches(3.20),width=Inches(4.15))
text(sl,.75,5.55,4.05,.9,'只选沟通对象、输入原话。\n背景与期望均留空，仍可生成表达。',17)
r=json.loads((A/'result.json').read_text())
text(sl,5.15,2.29,4.1,.38,'优化表达（简短版）',19,'C70019',True)
text(sl,5.15,2.86,4.15,1.75,'“'+r['concise']+'”',23,bold=True)
sl.shapes.add_picture(str(A/'expression-concise.png'),Inches(5.15),Inches(4.85),width=Inches(4.15))
text(sl,5.2,6.03,4.1,.6,'保留姓名、说明困扰、提出协调请求。',15,'C70019',True)
text(sl,.65,6.98,8.7,.18,'虚构情绪化示例，不作为对现实人物的评价｜真实界面；改写为本机替身数据，非真实模型效果实测',8,'727171')
text(sl,.54,7.1,.45,.23,'16',9,'727171')
row=rows[15];row.update(title='表达优化：保留具体指代，把抱怨转成诉求。',point='左侧读原话，两个可选框均留空；右侧先读大字简短表达，再对照实际生成截图。',speech='左边只选择沟通对象并输入原话，背景和期望都留空。这句话仅作为情绪化输入示例。右边是实际演示结果的简短版，我和朱彦霖的协作有些困扰，想请您帮忙梳理分歧、明确分工。简短不是把人物删掉，而是保留姓名和核心诉求，去掉人身评价。遇到信息不足，系统会提示补充具体事项，不补造同事行为。')
sl.notes_slide.notes_text_frame.text=f'【讲述稿】\n{row["speech"]}\n【看图指向】{row["point"]}\n【转场】{row["transition"]}'
prs.core_properties.title='AI职场沟通训练师｜第十三版 · 清晰的简短表达'
prs.save(ROOT/'AI-workplace-coach-story-v13.pptx');(ROOT/'story-v13-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
md=['# 第十三版讲述稿','','33页，第16页改为可选项留空、保留姓名的简短表达与大字结果。','']
for r in rows:md.extend([f'## {r["page"]:02d}｜{r["title"]}','','讲述：'+r['speech'],'','转场：'+r['transition'],''])
(ROOT/'项目展示内容与讲述稿-第十三版.md').write_text('\n'.join(md));print('v13 built:33 slides')
