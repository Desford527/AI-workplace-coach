"""Capture actual edit-profile dialog without changing user data or calling models."""
import os,sys,tempfile,threading,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'presentation/assets-v20';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'workplace-v5'));sys.argv=[sys.argv[0]];os.environ['COACH_DISABLE_BUNDLED_DEFAULTS']='1'
import server,workplace as w
with tempfile.TemporaryDirectory() as tmp:
 server.DATA_ROOT=tmp;server.CONFIG_PATH=str(Path(tmp)/'user_data/apiconfig.json');w.init(server.ROOT,tmp,server.CONFIG_PATH,server)
 http=server.http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);threading.Thread(target=http.serve_forever,daemon=True).start()
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True);page=browser.new_page(viewport={'width':1180,'height':1100},device_scale_factor=2,locale='zh-CN');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{http.server_port}');page.wait_for_function('ws!==null');page.click('[data-tab=objects]');page.click('[data-edit-object=builtin-project]');expect(page.locator('#objectDialog')).to_be_visible()
  page.locator('#objectDialog').evaluate('e=>e.scrollTop=0');page.locator('#objectDialog').screenshot(path=str(OUT/'edit-profile.png'))
  (OUT/'capture.json').write_text(json.dumps({'pageErrors':errors,'objectId':'builtin-project','interaction':'click 编辑画像','realModelCalls':0,'temporaryData':True},ensure_ascii=False,indent=2)+'\n');browser.close()
 http.shutdown()
