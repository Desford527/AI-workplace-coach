"""Unify all editable text and theme fonts to Microsoft YaHei without changing images."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import json
ROOT=Path(__file__).resolve().parent;SRC=ROOT/'AI-workplace-coach-story-v20.pptx';DST=ROOT/'AI-workplace-coach-story-v21.pptx'
A='http://schemas.openxmlformats.org/drawingml/2006/main';FONT='微软雅黑'
report={'font':FONT,'fontAttributesUpdated':0,'explicitFontNodesAdded':0,'symbolBulletsNormalized':0,'partsChanged':[]}
with ZipFile(SRC) as z:parts={n:z.read(n) for n in z.namelist()}
for name,raw in list(parts.items()):
 if not name.endswith('.xml'):continue
 t=E.fromstring(raw);changed=False
 for e in t.iter():
  if e.get('typeface') is not None:
   if E.QName(e).localname=='buFont' and e.get('typeface')=='Wingdings':
    bullet=e.getparent().find('{'+A+'}buChar')
    if bullet is not None:bullet.set('char','•');report['symbolBulletsNormalized']+=1
   e.set('typeface',FONT);report['fontAttributesUpdated']+=1;changed=True
 if name.startswith('ppt/'):
  for e in t.iter():
   if e.tag not in ['{'+A+'}rPr','{'+A+'}defRPr','{'+A+'}endParaRPr']:continue
   for tag in ['latin','ea','cs']:
    if e.find('{'+A+'}'+tag) is None:
     child=E.Element('{'+A+'}'+tag);child.set('typeface',FONT)
     order={'latin':0,'ea':1,'cs':2,'sym':3,'hlinkClick':4,'hlinkMouseOver':5,'rtl':6,'extLst':7}
     at=len(e)
     for i,n in enumerate(e):
      if E.QName(n).localname in order and order[E.QName(n).localname]>order[tag]:at=i;break
     e.insert(at,child);report['explicitFontNodesAdded']+=1;changed=True
 if changed:
  parts[name]=E.tostring(t,encoding='UTF-8',xml_declaration=True,standalone=True);report['partsChanged'].append(name)
with ZipFile(DST,'w',ZIP_DEFLATED) as z:
 for name,data in parts.items():z.writestr(name,data)
(ROOT/'story-v21-font-change.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('v21: font attributes',report['fontAttributesUpdated'],'explicit nodes added',report['explicitFontNodesAdded'])
