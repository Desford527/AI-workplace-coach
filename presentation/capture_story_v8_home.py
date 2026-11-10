"""Capture entire real homepage using isolated empty data, without model requests."""
import os,sys,tempfile,threading,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'presentation/assets-v8'
sys.path.insert(0,str(ROOT/'workplace-v5'));sys.argv=[sys.argv[0]]
os.environ['COACH_DISABLE_BUNDLED_DEFAULTS']='1'
import server,workplace as w
with tempfile.TemporaryDirectory() as tmp:
 server.DATA_ROOT=tmp;server.CONFIG_PATH=str(Path(tmp)/'user_data/apiconfig.json')
 w.init(server.ROOT,tmp,server.CONFIG_PATH,server)
 http=server.http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
 threading.Thread(target=http.serve_forever,daemon=True).start()
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True)
  page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=2,locale='zh-CN',timezone_id='Asia/Shanghai')
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{http.server_port}');page.wait_for_function('ws!==null');page.wait_for_timeout(500)
  page.screenshot(path=str(OUT/'home-full.png'),full_page=True)
  (OUT/'capture.json').write_text(json.dumps({'viewport':1440,'height':page.evaluate('document.documentElement.scrollHeight'),'pageErrors':errors,'realModelCalls':0},ensure_ascii=False,indent=2))
  browser.close()
 http.shutdown()
print((OUT/'capture.json').read_text())
