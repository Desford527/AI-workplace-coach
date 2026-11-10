"""Remove inherited bracket ornaments and rebuild every page number consistently."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import posixpath,json
ROOT=Path(__file__).resolve().parent;SRC=ROOT/'AI-workplace-coach-story-v21.pptx';DST=ROOT/'AI-workplace-coach-story-v22.pptx'
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';NS={'p':P,'a':A}
with ZipFile(SRC) as z:parts={n:z.read(n) for n in z.namelist()}
report={'ornamentsRemoved':[],'inheritedNumbersRemoved':[],'pageNumbers':[]}
# Clean template page-number frames and inherited page-number placeholders everywhere.
for name,data in list(parts.items()):
 if not name.endswith('.xml') or not name.startswith(('ppt/slides/','ppt/slideLayouts/','ppt/slideMasters/')):continue
 t=E.fromstring(data);changed=False
 for tree in t.xpath('//p:spTree',namespaces=NS):
  for sh in list(tree):
   names=sh.xpath('.//p:cNvPr/@name',namespaces=NS)
   if any('中括号' in s for s in names):
    tree.remove(sh);changed=True;report['ornamentsRemoved'].append({'part':name,'names':names});continue
   if sh.xpath('.//p:ph[@type="sldNum"]',namespaces=NS):
    tree.remove(sh);changed=True;report['inheritedNumbersRemoved'].append(name)
 if changed:parts[name]=E.tostring(t,encoding='UTF-8',xml_declaration=True,standalone=True)
pr=E.fromstring(parts['ppt/presentation.xml']);rels=E.fromstring(parts['ppt/_rels/presentation.xml.rels']);targets={r.get('Id'):r.get('Target') for r in rels}
ordered=[]
for sid in pr.find('p:sldIdLst',NS):
 target=targets[sid.get('{'+R+'}id')];ordered.append(target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('ppt',target)))
def element(tag,parent=None,**attrs):
 el=E.Element(tag) if parent is None else E.SubElement(parent,tag)
 for k,v in attrs.items():el.set(k,str(v))
 return el
for number,name in enumerate(ordered,1):
 t=E.fromstring(parts[name]);tree=t.find('p:cSld/p:spTree',NS)
 for sh in list(tree):
  content=''.join(sh.xpath('.//a:t/text()',namespaces=NS)).strip();off=sh.xpath('./p:spPr/a:xfrm/a:off',namespaces=NS)
  if content.isdigit() and off and int(off[0].get('y'))>6200000:tree.remove(sh)
 if number not in (1,len(ordered)):
  ident=max([int(v) for v in t.xpath('//p:cNvPr/@id',namespaces=NS)]+[0])+1
  shape=element('{'+P+'}sp',tree);nv=element('{'+P+'}nvSpPr',shape);element('{'+P+'}cNvPr',nv,id=ident,name='统一页码');element('{'+P+'}cNvSpPr',nv,txBox='1');element('{'+P+'}nvPr',nv)
  sp=element('{'+P+'}spPr',shape);xf=element('{'+A+'}xfrm',sp,rot='0');element('{'+A+'}off',xf,x=502920,y=6547104);element('{'+A+'}ext',xf,cx=411480,cy=219456)
  geom=element('{'+A+'}prstGeom',sp,prst='rect');element('{'+A+'}avLst',geom);element('{'+A+'}noFill',sp);element('{'+A+'}noFill',element('{'+A+'}ln',sp))
  body=element('{'+P+'}txBody',shape);element('{'+A+'}bodyPr',body,rot='0',vert='horz',wrap='none',lIns='0',tIns='0',rIns='0',bIns='0',anchor='ctr');element('{'+A+'}lstStyle',body)
  para=element('{'+A+'}p',body);pp=element('{'+A+'}pPr',para,marL='0',indent='0',algn='ctr',lvl='0');element('{'+A+'}buNone',pp)
  run=element('{'+A+'}r',para);rp=element('{'+A+'}rPr',run,lang='zh-CN',sz='1000',b='0',i='0',baseline='0');element('{'+A+'}srgbClr',element('{'+A+'}solidFill',rp),val='727171')
  for fonttag in ['latin','ea','cs']:element('{'+A+'}'+fonttag,rp,typeface='微软雅黑')
  element('{'+A+'}t',run).text=f'{number:02d}'
  report['pageNumbers'].append({'page':number,'x':502920,'y':6547104,'width':411480,'height':219456,'font':'微软雅黑','size':10,'rotation':0,'alignment':'center'})
 parts[name]=E.tostring(t,encoding='UTF-8',xml_declaration=True,standalone=True)
with ZipFile(DST,'w',ZIP_DEFLATED) as z:
 for name,data in parts.items():z.writestr(name,data)
(ROOT/'story-v22-numbering.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Rebuilt',len(report['pageNumbers']),'numbers; removed',len(report['ornamentsRemoved']),'bracket groups and',len(report['inheritedNumbersRemoved']),'inherited placeholders')
