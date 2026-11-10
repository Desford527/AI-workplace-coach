"""Actual overseas UI workflows with isolated fictional model responses, no real keys."""
import copy,json,os,sys,tempfile,threading
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'presentation/assets-v11';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'workplace-v5'));sys.path.insert(0,str(ROOT/'presentation'));sys.argv=[sys.argv[0]]
os.environ['COACH_DISABLE_BUNDLED_DEFAULTS']='1'
import server,workplace as w
from story_v4_demo import portrait_fixture
DATA=json.loads((ROOT/'workplace-v5/workplace-data.json').read_text())['overseasDemo'];CALLS=[]
def fixture(messages,review=False,config=None,validator=None):
 prompt=messages[0]['content'];source=messages[-1]['content'];CALLS.append('review' if '分析完整记录' in prompt else 'dialogue')
 if '长期沟通画像' in prompt:r=portrait_fixture(source)
 elif '分析完整记录' in prompt:
  msgs=json.loads(source);us=[m for m in msgs if m['role']=='user'];bs=[m for m in msgs if m['role']=='assistant']
  def dims(m,score):return [{'name':n,'score':score,'basis':'虚构演示：根据表达完整度给出协议样例分数，非真实模型评价。','evidence':[{'messageId':m['id'],'quote':m['text']}]} for n in w.DIMS]
  r={'summary':'承诺需保留验证边界，英语请求应更具体得体。','overall':'虚构演示：对照原句练习英语准确性与客户协作表达。','sampleLimit':'3条用户回应；演示替身生成，不能作为模型效果或英语等级证据。','dims':dims(us[-1],72),'timeline':[{'messageId':m['id'],'dims':dims(m,[42,54,78][i]),'feedback':DATA['turns'][i]['why'],'improved':DATA['turns'][i]['strong']} for i,m in enumerate(us)],'translations':[{'messageId':m['id'],**m['interpretation']} for m in bs],'loss':[{'title':'承诺边界与商务措辞','desc':'no problem 没有验证边界，命令式请求容易造成误解。','action':'先说明未验证条件，再明确澄清请求。'}],'next':['用英文完成一次“现状—边界—请求—更新节点”的交付说明。'],'language':'结合原句改写语法与商务措辞。','languageReview':{'summary':'英语练习聚焦语法、术语和得体请求，同时保留业务事实边界。','corrections':[{'messageId':us[0]['id'],'quote':us[0]['text'],'focus':'承诺边界 / 自然表达','improved':DATA['turns'][0]['strong'],'reason':DATA['turns'][0]['why']},{'messageId':us[1]['id'],'quote':us[1]['text'],'focus':'语法准确 / 商务得体','improved':DATA['turns'][1]['strong'],'reason':DATA['turns'][1]['why']}],'terms':DATA['glossary'],'practice':'用 Could you please…? 重写两条澄清请求；再用 I will send you an update by… 明确下一次更新。'}}
 else:
  i=sum(m['role']=='user' and not m['content'].startswith('请按上述工作场景和目标开始会议') for m in messages);r={'line':DATA['turns'][min(i,2)]['customer'] if i<3 else 'Thank you. Please include the remaining validation risks in your next update.','surface':'确认交期、验收条件或后续更新安排。','real':'客户需要据此安排安装与资源。','hidden':'模拟判断依据：信息是否具体，承诺是否有证据与边界。'}
 return validator(r) if validator else r
with tempfile.TemporaryDirectory() as tmp:
 server.DATA_ROOT=tmp;server.CONFIG_PATH=str(Path(tmp)/'user_data/apiconfig.json');w.init(server.ROOT,tmp,server.CONFIG_PATH,server);w.ask=fixture
 w.atomic_config({'apis':[{'id':'overseas-demo','name':'本机虚构演示','baseURL':'http://127.0.0.1:9/v1','apiKey':'','model':'fixture','useLLM':True}],'active':'overseas-demo'})
 http=server.http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);threading.Thread(target=http.serve_forever,daemon=True).start()
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True)
  page=browser.new_page(viewport={'width':1180,'height':900},device_scale_factor=2,locale='zh-CN',timezone_id='Asia/Shanghai');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{http.server_port}');page.wait_for_function('ws!==null')
  assert page.locator('#overseasDemo').is_hidden()
  page.click('[data-category=english]');page.click('[data-scene=en-delay]');expect(page.locator('#overseasDemo')).to_be_visible()
  page.locator('#overseasDemo details').evaluate('e=>e.open=true');page.locator('#overseasDemo').screenshot(path=str(OUT/'overseas-example.png'))
  cut=page.locator('.language-example').nth(1).evaluate("e=>(e.getBoundingClientRect().top-document.getElementById('overseasDemo').getBoundingClientRect().top)*2")
  (OUT/'example-layout.json').write_text(json.dumps({'splitY':round(cut)}))
  page.click('#loadOverseasGoal');expect(page.locator('#goal')).to_have_value(DATA['goal']);page.click('#start');expect(page.locator('#chat .bubble')).to_have_count(1)
  replies=[DATA['turns'][0]['weak'],DATA['turns'][1]['weak'],DATA['turns'][2]['strong']]
  for i,t in enumerate(replies):
   page.fill('#reply',t);page.click('#send');expect(page.locator('#chat .bubble')).to_have_count(3+2*i)
  page.locator('#chat').evaluate('e=>{e.style.maxHeight="none";e.scrollTop=0}');page.locator('#chat').screenshot(path=str(OUT/'overseas-dialogue.png'))
  page.click('#end');expect(page.locator('.language-review')).to_be_visible();expect(page.locator('.language-correction')).to_have_count(2)
  page.locator('.language-review').screenshot(path=str(OUT/'language-review.png'));page.locator('.review-head').screenshot(path=str(OUT/'overseas-score.png'))
  page.locator('.round').first.screenshot(path=str(OUT/'overseas-round.png'))
  page.locator('#workspace').screenshot(path=str(OUT/'nav-practice.png'))
  with page.expect_download() as exported:page.click('#exportHTML')
  exported_text=Path(exported.value.path()).read_text()
  assert '英语表达提升' in exported_text and 'Could you please confirm' in exported_text
  page.set_viewport_size({'width':390,'height':844})
  assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'), 'mobile overflow'
  page.locator('.language-review').screenshot(path=str(OUT/'language-mobile.png'))
  sample=page.evaluate('session');assert sample['review']['languageReview']['corrections'][1]['quote']==replies[1]
  (OUT/'session.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2)+'\n')
  (OUT/'acceptance.json').write_text(json.dumps({'pageErrors':errors,'validatedModelCalls':len(CALLS),'realModelCalls':0,'userReplies':3,'languageCorrections':2,'mobile390NoOverflow':True,'htmlExportIncludesLanguage':True,'sixAxisScore':sample['review']['score'],'foreignDemoHiddenForChinese':True,'loadGoalAndBackground':True},ensure_ascii=False,indent=2)+'\n')
  print((OUT/'acceptance.json').read_text());browser.close()
 http.shutdown()
