"""Restore original bracket frames and center the page number inside each frame."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import copy,json
ROOT=Path(__file__).resolve().parent;SRC=ROOT/'AI-workplace-coach-story-v22.pptx';DST=ROOT/'AI-workplace-coach-story-v23.pptx'
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main';NS={'p':P,'a':A}
with ZipFile(SRC) as z:parts={n:z.read(n) for n in z.namelist()}
with ZipFile(ROOT/'AI-workplace-coach-story-v21.pptx') as z:
 master=E.fromstring(z.read('ppt/slideMasters/slideMaster1.xml'))
 frame=next(g for g in master.xpath('//p:spTree/p:grpSp',namespaces=NS) if any('中括号' in name for name in g.xpath('.//p:cNvPr/@name',namespaces=NS)))
xf=frame.find('p:grpSpPr/a:xfrm',NS);off=xf.find('a:off',NS);ext=xf.find('a:ext',NS)
report={'frameSource':'v21 original template bracket group','frames':0,'bounds':{'x':int(off.get('x')),'y':int(off.get('y')),'width':int(ext.get('cx')),'height':int(ext.get('cy'))}}
for name,raw in list(parts.items()):
 if not name.startswith('ppt/slides/') or not name.endswith('.xml'):continue
 t=E.fromstring(raw);nums=t.xpath('//p:spTree/p:sp[p:nvSpPr/p:cNvPr[@name="统一页码"]]',namespaces=NS)
 if not nums:continue
 assert len(nums)==1
 number=nums[0];tree=number.getparent();g=copy.deepcopy(frame)
 ident=max([int(v) for v in t.xpath('//p:cNvPr/@id',namespaces=NS)]+[0])+1
 for c in g.xpath('.//p:cNvPr',namespaces=NS):c.set('id',str(ident));ident+=1
 g.find('p:nvGrpSpPr/p:cNvPr',NS).set('name','页码框')
 for c in g.xpath('.//a:ln/a:solidFill/a:schemeClr',namespaces=NS):
  c.tag='{'+A+'}srgbClr';c.attrib.clear();c.set('val','B4B4B4')
 tree.insert(tree.index(number),g)
 tx=number.find('p:spPr/a:xfrm',NS);tx.find('a:off',NS).attrib.update(off.attrib);tx.find('a:ext',NS).attrib.update(ext.attrib)
 body=number.find('p:txBody/a:bodyPr',NS);body.set('anchor','ctr');body.set('wrap','none')
 for k in ['lIns','rIns','tIns','bIns']:body.set(k,'0')
 pp=number.find('p:txBody/a:p/a:pPr',NS);pp.set('algn','ctr')
 for tag in ['lnSpc','spcBef','spcAft']:
  old=pp.find('a:'+tag,NS)
  if old is not None:pp.remove(old)
  el=E.Element('{'+A+'}'+tag);sub=E.SubElement(el,'{'+A+'}'+('spcPct' if tag=='lnSpc' else 'spcPts'));sub.set('val','100000' if tag=='lnSpc' else '0');pp.insert(['lnSpc','spcBef','spcAft'].index(tag),el)
 parts[name]=E.tostring(t,encoding='UTF-8',xml_declaration=True,standalone=True);report['frames']+=1
with ZipFile(DST,'w',ZIP_DEFLATED) as z:
 for name,data in parts.items():z.writestr(name,data)
(ROOT/'story-v23-numbering.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Restored',report['frames'],'original bracket frames; numbers centered in matching bounds')
