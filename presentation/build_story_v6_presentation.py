"""Correct title/navigation order and keep navigation only where it matches content."""
from pathlib import Path
import hashlib,json,re
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.xmlchemy import OxmlElement

ROOT=Path(__file__).resolve().parent
prs=Presentation(ROOT/'AI-workplace-coach-story-v5.pptx')
content=json.loads((ROOT/'story-v5-content.json').read_text())
nav_hashes={}
for folder in ['assets-v3','assets-v4','assets-v5']:
 for p in (ROOT/folder).glob('nav-*.png'):
  nav_hashes[hashlib.sha256(p.read_bytes()).digest()]=p.stem.removeprefix('nav-')

# These entries are global controls or span two destinations, rather than a workspace tab.
CONTEXT={
 6:'右上角「API 设置」 · 配置服务地址与对话、复盘模型',
 17:'页面底部「导入会议纪要」 · 文件导入与正文粘贴',
 18:'「导入会议纪要」中的提取预览 · 核对人物、项目与经验',
 20:'已保存的项目背景 · 在训练页选择并引用',
 22:'页面底部「想改什么，直接说」 · 新增对象',
 23:'页面底部「想改什么，直接说」 · 补充画像与语录',
 24:'页面底部「想改什么，直接说」 · 调整追问强度',
 25:'页面底部「想改什么，直接说」 · 收录沟通经验',
}
KEPT={**{i:'practice' for i in range(7,14)},**{i:'portrait' for i in range(14,17)},19:'objects',21:'experiences',26:'history',27:'objects'}

def caption(sl,value):
 sh=sl.shapes.add_textbox(Inches(.65),Inches(1.86),Inches(8.7),Inches(.34))
 tf=sh.text_frame;tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 p=tf.paragraphs[0];r=p.add_run();r.text=value;r.font.name='Noto Sans CJK SC';r.font.size=Pt(13);r.font.bold=True;r.font.color.rgb=RGBColor.from_string('C70019')
 ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)

changes=[]
for page,(sl,row) in enumerate(zip(prs.slides,content),1):
 nav=[]
 for sh in sl.shapes:
  if sh.shape_type==MSO_SHAPE_TYPE.PICTURE:
   tab=nav_hashes.get(hashlib.sha256(sh.image.blob).digest())
   if tab:nav.append((sh,tab))
 if not nav:continue
 title=next(sh for sh in sl.shapes if sh.has_text_frame and sh.text==row['title'])
 title.top=Inches(1.02);title.height=Inches(.56)
 if page in CONTEXT:
  for sh,_ in nav:sl.shapes._spTree.remove(sh._element)
  if page==6:
   # The API body already labels the actual global settings entry; no workspace directory.
   for sh in sl.shapes:
    if sh.has_text_frame and '入口在右上角' in sh.text:
     sh.top=Inches(1.86)
    elif Inches(2.75)<=sh.top<Inches(6.25):
     sh.top-=Inches(.30)
  else:caption(sl,CONTEXT[page])
  row['point']=re.sub(r'导航选中[“”\w\u4e00-\u9fff]+；','',row['point'])
  row['point']=CONTEXT[page]+'。'+row['point']
  changes.append({'page':page,'navigation':'removed','context':CONTEXT[page]})
 else:
  assert len(nav)==1 and nav[0][1]==KEPT[page],(page,nav)
  nav[0][0].top=Inches(1.67)
  assert title.top+title.height<nav[0][0].top
  changes.append({'page':page,'navigation':'below_title','tab':nav[0][1]})
 sl.notes_slide.notes_text_frame.text=f'【建议停留】{row["seconds"]}秒\n【本页一句话】{row["body"]}\n【看图指向】{row["point"] or "按页面顺序讲述"}\n【讲述稿】\n{row["speech"]}\n【转场】\n{row["transition"]}'

prs.core_properties.title='AI职场沟通训练师｜第六版 · 主标题优先与页面对应'
prs.core_properties.subject='移除API等全局入口的不对应标签栏，相关目录移至主标题下方'
prs.save(ROOT/'AI-workplace-coach-story-v6.pptx')
(ROOT/'story-v6-content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
(ROOT/'story-v6-layout.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
md=['# AI职场沟通训练师｜第六版讲述稿','','沿用第五版30页内容与功能顺序。第6页API设置不再放工作区标签栏；纪要、自由输入等全局入口改为对应的入口说明。其余相关标签栏全部移到主标题下方。保留截图本身自带的真实目录。','','主讲约14分钟。API设置第6页；四组直接说输入/效果对照第22–25页。案例、评分及分析为本机演示数据，不代表真实模型效果。','']
for c in content:
 md.extend([f'## {c["page"]:02d}｜{c["title"]}','','**本页重点**：'+c['body'],'',f'**建议停留**：{c["seconds"]}秒','','**看图指向**：'+(c['point'] or '按页面顺序讲述'),'','**讲述稿**','',c['speech'],'','**转场**','',c['transition'],''])
(ROOT/'项目展示内容与讲述稿-第六版.md').write_text('\n'.join(md))
print('Built v6:',len(prs.slides),'pages;',sum(c['navigation']=='removed' for c in changes),'irrelevant strips removed;',sum(c['navigation']=='below_title' for c in changes),'relevant strips below headline.')
