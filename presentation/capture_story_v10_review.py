"""Capture real review report using isolated empty data, without model requests."""
import os,sys,tempfile,threading,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'presentation/assets-v10'
OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'workplace-v5'));sys.argv=[sys.argv[0]]
os.environ['COACH_DISABLE_BUNDLED_DEFAULTS']='1'
import server,workplace as w
with tempfile.TemporaryDirectory() as tmp:
 server.DATA_ROOT=tmp;server.CONFIG_PATH=str(Path(tmp)/'user_data/apiconfig.json')
 w.init(server.ROOT,tmp,server.CONFIG_PATH,server)
 sample=json.loads((ROOT/'presentation/assets-v5/primary-review.json').read_text());w.save('session',sample['id'],sample)
 http=server.http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
 threading.Thread(target=http.serve_forever,daemon=True).start()
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True)
  page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=2,locale='zh-CN',timezone_id='Asia/Shanghai')
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{http.server_port}');page.wait_for_function('ws!==null');page.wait_for_timeout(500)
  page.evaluate('(id)=>openSession(id)',sample['id']);page.wait_for_selector('.bigscore')
  page.locator('.round').last.evaluate('(e)=>e.open=true')
  page.locator('#workspace').evaluate("e=>e.scrollIntoView({block:'start',behavior:'instant'})")
  a=page.locator('#workspace').bounding_box();b=page.locator('#sessionPanel').bounding_box()
  page.screenshot(path=str(OUT/'review-full.png'),full_page=True,clip={'x':a['x'],'y':a['y'],'width':a['width'],'height':b['y']+b['height']-a['y']})
  (OUT/'capture.json').write_text(json.dumps({'source':'assets-v5/primary-review.json','pageErrors':errors,'realModelCalls':0,'splitY':round(page.locator('.round').first.evaluate('(e)=>(e.parentElement.getBoundingClientRect().top+window.scrollY)*2')),'sampleReplies':sum(m['role']=='user' for m in sample['messages'])},ensure_ascii=False,indent=2))
  browser.close()
 http.shutdown()
print((OUT/'capture.json').read_text())
