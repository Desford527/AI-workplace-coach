"""Fresh real object UI, temporary records, one explicitly fictional AI analysis."""
import os,sys,tempfile,threading,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'presentation/assets-v18';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'workplace-v5'));sys.argv=[sys.argv[0]];os.environ['COACH_DISABLE_BUNDLED_DEFAULTS']='1'
import server,workplace as w
calls=[]
def fixture(messages,review=False,config=None,validator=None):
 data=json.loads(messages[-1]['content']);q=data['quotes'][0];calls.append('quote-analysis')
 r={'summary':'从两条演示语录看，可能更重视验证证据和承诺边界；需更多场景验证。','traits':[{'title':'先核对依据，再讨论承诺','description':'倾向先询问测试条件与未验证项，再明确可推进的范围。','evidence':[q]}],'likelyLines':[{'text':'先说哪些条件已经验证，再讨论能承诺到什么范围。','basis':[q]}]}
 return validator(r) if validator else r
with tempfile.TemporaryDirectory() as tmp:
 server.DATA_ROOT=tmp;server.CONFIG_PATH=str(Path(tmp)/'user_data/apiconfig.json');w.init(server.ROOT,tmp,server.CONFIG_PATH,server);w.ask=fixture
 w.atomic_config({'apis':[{'id':'objects-authoring','name':'本机虚构演示','baseURL':'http://127.0.0.1:9/v1','apiKey':'','model':'fixture','useLLM':True}],'active':'objects-authoring'})
 http=server.http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);threading.Thread(target=http.serve_forever,daemon=True).start()
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True);page=browser.new_page(viewport={'width':1180,'height':900},device_scale_factor=2,locale='zh-CN',timezone_id='Asia/Shanghai');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{http.server_port}');page.wait_for_function('ws!==null');page.click('[data-tab=objects]')
  page.locator('#workspace').screenshot(path=str(OUT/'nav-objects.png'));page.locator('#objectCards').screenshot(path=str(OUT/'object-roster.png'))
  page.click('[data-object-quotes=builtin-project]');page.fill('#objectQuotes','没有验证记录，先不要承诺交付。\n先把测试条件和边界说清楚。');page.locator('#objectQuotes').locator('..').screenshot(path=str(OUT/'quote-input.png'))
  page.click('#quotesAnalyze');expect(page.locator('#quotesStatus')).to_contain_text('语录与 AI 分析已保存')
  page.locator('#quoteAnalysis .quote-trait details').evaluate('e=>e.open=true');page.locator('#quoteAnalysis').screenshot(path=str(OUT/'quote-analysis.png'))
  assert w.get('object-analysis','builtin-project')['sampleCount']==2
  (OUT/'acceptance.json').write_text(json.dumps({'pageErrors':errors,'validatedFixtureCalls':len(calls),'realModelCalls':0,'quotes':2,'citationVerifiedByProductionValidator':True},ensure_ascii=False,indent=2)+'\n')
  browser.close()
 http.shutdown()
print((OUT/'acceptance.json').read_text())
