"""Real expression UI, explicit local Chat Completions double, no real API keys."""
import os,sys,tempfile,threading,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'presentation/assets-v13';OUT.mkdir(exist_ok=True)
sys.path[:0]=[str(ROOT/'workplace-v5'),str(ROOT/'workplace-v5/tests')];sys.argv=[sys.argv[0]];os.environ['COACH_DISABLE_BUNDLED_DEFAULTS']='1'
import server,workplace as w
from fake_provider import start,Provider
with tempfile.TemporaryDirectory() as tmp:
 server.DATA_ROOT=tmp;server.CONFIG_PATH=str(Path(tmp)/'user_data/apiconfig.json');w.init(server.ROOT,tmp,server.CONFIG_PATH,server)
 provider=start();w.atomic_config({'apis':[{'id':'expression-demo','name':'本机替身演示','baseURL':f'http://127.0.0.1:{provider.server_port}/v1','apiKey':'','model':'fixture','useLLM':True}],'active':'expression-demo'})
 http=server.http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);threading.Thread(target=http.serve_forever,daemon=True).start()
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True);context=browser.new_context(viewport={'width':1180,'height':900},device_scale_factor=2,locale='zh-CN');context.grant_permissions(['clipboard-read','clipboard-write'])
  page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{http.server_port}');page.wait_for_function('ws!==null')
  page.click('[data-tab=expression]');expect(page.locator('#expression')).to_be_visible();page.select_option('#expressionObject','builtin-project');page.fill('#expressionText','我觉得朱彦霖脑子有问题')
  expect(page.locator('#expressionGoal')).to_have_value('');expect(page.locator('#expressionContext')).to_have_value('')
  page.locator('#expressionForm').screenshot(path=str(OUT/'expression-input.png'));page.locator('#workspace').screenshot(path=str(OUT/'nav-expression.png'))
  page.click('#expressionSubmit');expect(page.locator('.expression-output')).to_be_visible();expect(page.locator('#expressionStatus')).to_contain_text('已生成')
  expect(page.locator('.expression-output')).to_contain_text('朱彦霖');page.locator('.expression-output').screenshot(path=str(OUT/'expression-result.png'))
  assert '朱彦霖' in page.evaluate('expressionOutput.concise')
  (OUT/'result.json').write_text(json.dumps(page.evaluate('expressionOutput'),ensure_ascii=False,indent=2)+'\n')
  page.locator('.expression-output .answer-box').nth(1).screenshot(path=str(OUT/'expression-concise.png'))
  page.click('[data-copy-expression=professional]');assert '协作' in page.evaluate('navigator.clipboard.readText()')
  Provider.mode='payment';page.click('#expressionSubmit');expect(page.locator('#expressionStatus')).to_contain_text('402');expect(page.locator('#expressionText')).to_have_value('我觉得朱彦霖脑子有问题');expect(page.locator('.expression-output')).to_be_visible()
  Provider.mode='ok';page.select_option('#expressionObject','general');page.select_option('#expressionLanguage','en');page.click('#expressionSubmit');expect(page.locator('#expressionStatus')).to_contain_text('已生成');expect(page.locator('.expression-output')).to_contain_text('Could we')
  page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not w.all_docs('session') and not w.all_docs('command')
  report={'pageErrors':errors,'copy':True,'http402PreservesInputAndPreviousResult':True,'genericAndEnglish':True,'mobile390':True,'noProfileOrSessionChanges':True,'optionalFieldsEmpty':True,'concisePreservesPerson':True,'realModelCalls':0}
  (OUT/'acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(report);browser.close()
 http.shutdown();provider.shutdown()
