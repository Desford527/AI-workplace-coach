"""Remove speaker notes, off-canvas template instructions, animations and transitions."""
from pathlib import Path
import json,posixpath
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'AI-workplace-coach-story-v18.pptx';DST=ROOT/'AI-workplace-coach-story-v19.pptx'
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main';NS={'p':P,'a':A}
with ZipFile(SRC) as z:parts={n:z.read(n) for n in z.namelist()}
pr=E.fromstring(parts['ppt/presentation.xml']);sz=pr.find('p:sldSz',NS);w,h=int(sz.get('cx')),int(sz.get('cy'))
removed_parts={n for n in parts if n.startswith(('ppt/notesSlides/','ppt/notesMasters/'))}
report={'source':SRC.name,'output':DST.name,'offCanvasObjects':[],'effectsRemoved':[],'notePartsRemoved':len(removed_parts),'noteRelationsRemoved':0}
for n in list(parts):
 if n in removed_parts:del parts[n];continue
 if not n.endswith(('.xml','.rels')):continue
 t=E.fromstring(parts[n]);changed=False
 if n.endswith('.rels'):
  for rel in list(t):
   if rel.get('Type','').rsplit('/',1)[-1] in ('notesSlide','notesMaster'):
    t.remove(rel);report['noteRelationsRemoved']+=1;changed=True
 elif n=='[Content_Types].xml':
  for child in list(t):
   if child.get('PartName','').lstrip('/') in removed_parts:t.remove(child);changed=True
 elif n.startswith('ppt/'):
  for el in list(t.iter()):
   if E.QName(el).localname in ('timing','transition','notesMasterIdLst'):
    parent=el.getparent()
    if parent is not None:
     parent.remove(el);changed=True
     if E.QName(el).localname!='notesMasterIdLst':report['effectsRemoved'].append({'part':n,'element':E.QName(el).localname})
  if n.startswith(('ppt/slides/','ppt/slideLayouts/','ppt/slideMasters/')):
   for tree in t.xpath('//p:spTree',namespaces=NS):
    for sh in list(tree):
     if E.QName(sh).localname not in ('sp','pic','grpSp','graphicFrame','cxnSp'):continue
     xf=sh.xpath('./p:spPr/a:xfrm|./p:grpSpPr/a:xfrm|./p:xfrm',namespaces=NS)
     if not xf:continue
     off=xf[0].find('a:off',NS);ext=xf[0].find('a:ext',NS)
     if off is None or ext is None:continue
     x,y=int(off.get('x')),int(off.get('y'));cx,cy=int(ext.get('cx')),int(ext.get('cy'))
     if x>=w or y>=h or x+cx<=0 or y+cy<=0:
      report['offCanvasObjects'].append({'part':n,'text':''.join(sh.xpath('.//a:t/text()',namespaces=NS))})
      tree.remove(sh);changed=True
 if changed:parts[n]=E.tostring(t,encoding='UTF-8',xml_declaration=True,standalone=True)
with ZipFile(DST,'w',ZIP_DEFLATED) as z:
 for n,data in parts.items():z.writestr(n,data)
(ROOT/'story-v19-cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Removed:',len(report['offCanvasObjects']),'off-canvas objects,',len(report['effectsRemoved']),'animation/transition nodes,',report['notePartsRemoved'],'note parts')
