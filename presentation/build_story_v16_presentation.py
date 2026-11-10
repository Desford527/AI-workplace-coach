"""Portable Skill evidence and GitHub closing page; voice demo is user-recorded later."""
from pathlib import Path
import json
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
ROOT=Path(__file__).resolve().parent;A=ROOT/'assets-v16';prs=Presentation(ROOT/'AI-workplace-coach-story-v15.pptx');rows=json.loads((ROOT/'story-v15-content.json').read_text())
def text(sl,x,y,w,h,s,size=18,color='4C4948',bold=False,url=None):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 for i,line in enumerate(s.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();r=p.add_run();r.text=line;r.font.name='Noto Sans CJK SC';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
  ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)
  if url:r.hyperlink.address=url
 return sh
from PIL import Image
sl=prs.slides[34]
for sh in list(sl.shapes):
 if sh!=sl.shapes.title:sl.shapes._spTree.remove(sh._element)
text(sl,.55,1.02,9,.55,'项目已公开发布，欢迎下载体验。',25,bold=True)
text(sl,.7,1.8,4.2,.32,'GitHub 公开仓库',16,'C70019',True)
text(sl,5.05,1.8,4.3,.32,'项目说明与下载入口',16,'C70019',True)
sl.shapes.add_picture(str(ROOT/'assets-v15/github-styled.png'),Inches(.7),Inches(2.25),width=Inches(4.1))
text(sl,.8,4.65,3.95,1.38,'下载本地应用\n查看启动与使用说明\n获取 Skill 和演示资料',20,bold=True)
sl.shapes.add_picture(str(A/'project-readme-user.png'),Inches(5.05),Inches(2.25),width=Inches(4.3))
url='https://github.com/Desford527/AI-workplace-coach'
text(sl,.8,6.55,8.4,.35,'github.com/Desford527/AI-workplace-coach',19,'C70019',True,url)
text(sl,.75,7.0,8.7,.16,'左：实际仓库内容简洁视图；右：用户提供的项目说明原图。',8,'727171')
text(sl,.54,7.1,.45,.23,'35',9,'727171')
row=rows[34];row['point']='左边是公开仓库，右边是项目说明及下载入口，下方链接可点击。';row['speech']='项目已经在GitHub公开。左边是仓库，右边是项目说明与下载入口，可以下载本地应用、查看启动方式，也可以获取Skill和演示资料，欢迎大家体验。'
sl.notes_slide.notes_text_frame.text=f'【讲述】\n{row["speech"]}\n【转场】\n{row["transition"]}'
prs.core_properties.title='AI职场沟通训练师｜第十六版 · 发布页项目说明'
prs.save(ROOT/'AI-workplace-coach-story-v16.pptx');(ROOT/'story-v16-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
md=['# 第十六版讲述稿','','36页，仅第35页发布页更新：仓库截图与用户提供的说明图左右展示。','']
for r in rows:md.extend([f'## {r["page"]:02d}｜{r["title"]}','','讲述：'+r['speech'],'','转场：'+r['transition'],''])
(ROOT/'项目展示内容与讲述稿-第十六版.md').write_text('\n'.join(md));print('v16 built: 36 pages')
