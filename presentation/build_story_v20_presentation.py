"""Replace slide05 commentary with a real screenshot of the edit-profile dialog."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches
from PIL import Image
ROOT=Path(__file__).resolve().parent
prs=Presentation(ROOT/'AI-workplace-coach-story-v19.pptx');sl=prs.slides[4]
removed=[]
for sh in list(sl.shapes):
 if sh.has_text_frame and sh.left>=Inches(5.8) and sh.top>=Inches(2.3):
  removed.append(sh.text);sl.shapes._spTree.remove(sh._element)
assert len(removed)==4
path=ROOT/'assets-v20/edit-profile.png';iw,ih=Image.open(path).size
h=4.67;w=h*iw/ih
sl.shapes.add_picture(str(path),Inches(5.85+(3.5-w)/2),Inches(2.36),height=Inches(h))
prs.core_properties.title='AI职场沟通训练师｜第二十版 · 编辑对象画像截图'
prs.save(ROOT/'AI-workplace-coach-story-v20.pptx')
print('v20 built:38 pages, slide05 right text replaced by actual edit dialog')
