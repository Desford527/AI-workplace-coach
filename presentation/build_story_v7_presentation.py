"""Embed the overview MP4 after the preserved cover; keep the v6 slide layout."""
from pathlib import Path
import json
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
from pptx.opc.packuri import PackURI

ROOT=Path(__file__).resolve().parent
prs=Presentation(ROOT/'AI-workplace-coach-story-v6.pptx')
rows=json.loads((ROOT/'story-v6-content.json').read_text())
manifest=json.loads((ROOT/'video-v7/manifest.json').read_text())
duration=manifest['duration']

def text(sl,x,y,w,h,value,size=20,color='4C4948',bold=False):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.clear();tf.word_wrap=True
 tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 p=tf.paragraphs[0];r=p.add_run();r.text=value;r.font.name='Noto Sans CJK SC';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
 ea=OxmlElement('a:ea');ea.set('typeface','Noto Sans CJK SC');r._r.get_or_add_rPr().append(ea)
 return sh

sl=prs.slides.add_slide(prs.slide_layouts[2]);sl.part.partname=PackURI('/ppt/slides/slide2001.xml')
for sh in list(sl.shapes):
 if sh!=sl.shapes.title:sl.shapes._spTree.remove(sh._element)
sl.shapes.title.text='开场视频  网页总览'
for r in sl.shapes.title.text_frame.paragraphs[0].runs:r.font.name='Noto Sans CJK SC';r.font.size=Pt(24);r.font.bold=True;r.font.color.rgb=RGBColor.from_string('4C4948')
text(sl,.55,1.02,8.9,.46,'39秒看一遍网页全貌 · 点击画面播放',25,bold=True)
# Keep a normal poster underneath for viewers/PDF exporters that ignore video posters.
sl.shapes.add_picture(str(ROOT/'video-v7/poster.png'),Inches(.80),Inches(1.72),width=Inches(8.40),height=Inches(8.40*816/1280))
movie=sl.shapes.add_movie(str(ROOT/'video-v7/AI-workplace-coach-overview-v7.mp4'),Inches(.80),Inches(1.72),Inches(8.40),Inches(8.40*816/1280),poster_frame_image=str(ROOT/'video-v7/poster.png'),mime_type='video/mp4')
text(sl,1.25,7.16,8.0,.18,'字幕版，无配音 · PPT中点击画面播放；PDF仅显示封面 · 另附独立MP4',9,'727171')
sid=prs.slides._sldIdLst[-1];prs.slides._sldIdLst.remove(sid);prs.slides._sldIdLst.insert(1,sid)
rows.insert(1,{'page':2,'title':'39秒网页总览','body':'用真实网页操作快速看见训练、复盘、画像、经验、纪要和直接说。','seconds':40,'point':'切到此页后点击视频画面播放；字幕在网页下方，不遮挡操作。','speech':'先用一段约39秒的录屏，看看网页的整体结构。画面中的对话、分数和办理结果为本机演示数据。','transition':'刚才看到了产品，下面从它要解决的工作问题说起。','appendix':False})
rows[0]['speech']='大家好，今天介绍 AI职场沟通训练师。先用一段简短录屏看一下网页全貌，再说明项目的背景、功能和实际演示。'
rows[0]['transition']='请看这段约39秒的网页总览。'
for i,(slide,row) in enumerate(zip(prs.slides,rows),1):
 row['page']=i
 slide.notes_slide.notes_text_frame.text=f'【建议停留】{row["seconds"]}秒\n【本页一句话】{row["body"]}\n【看图指向】{row["point"] or "按页面顺序讲述"}\n【讲述稿】\n{row["speech"]}\n【转场】\n{row["transition"]}'
 for sh in list(slide.shapes):
  if sh.has_text_frame and sh.text.strip().isdigit() and sh.top>Inches(7):slide.shapes._spTree.remove(sh._element)
 if i not in [1,len(rows)]:text(slide,.54,7.1,.45,.23,str(i).zfill(2),9,'727171')
prs.core_properties.title='AI职场沟通训练师｜第七版 · 网页总览开场视频'
prs.core_properties.subject='封面后嵌入39秒真实网页录屏，保留第六版主标题与目录对应布局'
prs.save(ROOT/'AI-workplace-coach-story-v7.pptx')
(ROOT/'story-v7-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
md=['# 第七版讲述稿与视频开场','','第2页嵌入约39秒的网页总览，点击画面播放。MP4已嵌入，不依赖外链。字幕放在网页画面下方；本版无配音。PDF只显示视频封面。','','原第六版其余内容顺延一页：API设置第7页，直接说四组对照第23–26页。共31页，完整讲述约14–15分钟。','','## 视频字幕脚本','']
for item in manifest['timeline']:md.extend([f'{item["start"]:04.1f}–{item["end"]:04.1f}秒：{item["caption"]}',''])
for row in rows:md.extend([f'## {row["page"]:02d}｜{row["title"]}','','**本页重点**：'+row['body'],'',f'**建议停留**：{row["seconds"]}秒','','**看图指向**：'+(row['point'] or '按页面顺序讲述'),'','**讲述稿**','',row['speech'],'','**转场**','',row['transition'],''])
(ROOT/'项目展示内容与讲述稿-第七版.md').write_text('\n'.join(md))
print('Built v7:',len(prs.slides),'pages; embedded overview on page 2;',duration,'seconds.')
