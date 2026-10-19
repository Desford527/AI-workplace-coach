"""Capture actual product workflows with isolated, deterministic authoring fixtures.
Only this authoring process replaces ask(); application source/default Key stay unchanged.
All sample texts and scores are fictional, not real-model or business-effect evidence.
"""
import copy,json,os,pathlib,socket,sys,tempfile,threading,time,urllib.request
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(__file__).resolve().parents[1];APP=ROOT/'workplace-v5';OUT=ROOT/'presentation/assets-v4';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(APP));sys.argv=[sys.argv[0]]
os.environ['COACH_DISABLE_BUNDLED_DEFAULTS']='1'
import server
import workplace as w
from story_v4_demo import TRAININGS, dialogue_fixture, review_fixture, portrait_fixture
DIMS=w.DIMS
MINUTES='会议：A项目周例会\n朱总（项目负责人）：“没有验证记录，先不要承诺交付。”\n朱总要求先核实高温验证与测试条件。\n王工（测试负责人）：“我周三补齐验证记录。”\nA项目：高温验证尚未完成；王工周三补齐报告，周四确认交付计划。\n决议：先说明未验证项，再决定交付范围。'
CALLS=[]
def fixture_ask(messages,review=False,config=None,validator=None):
 prompt=messages[0]['content'];source=messages[-1]['content']
 if '会议纪要提取助手' in prompt:
  CALLS.append('会议纪要提取')
  result={'summary':'本次会议围绕验证边界与交付决策展开，需补齐验证记录后再明确交付范围。','items':[
   {'kind':'observation','name':'朱总','role':'项目负责人','field':'standards','certainty':'observed','text':'交付判断需要先核实验证记录和适用条件。','evidence':['朱总要求先核实高温验证与测试条件。']},
   {'kind':'quote','name':'朱总','role':'项目负责人','text':'没有验证记录，先不要承诺交付。','evidence':['朱总（项目负责人）：“没有验证记录，先不要承诺交付。”']},
   {'kind':'project','name':'A项目','text':'高温验证尚未完成；王工周三补齐验证报告，周四再确认交付计划。','evidence':['A项目：高温验证尚未完成；王工周三补齐报告，周四确认交付计划。']},
   {'kind':'experience','title':'先明确验证边界，再承诺交付','category':'项目汇报','content':'当验证尚未闭环时，先说明已知与未知项，再明确可交付范围、责任人及下一次同步时间，最后提出需要对方决定的事项。','evidence':['决议：先说明未验证项，再决定交付范围。']}]}
 elif '分析对象语录' in prompt:
  CALLS.append('语录分析');data=json.loads(source);q=data['quotes'][0]
  result={'summary':'从少量语录看，对方可能偏好有依据的判断与明确的风险边界；仍需更多场景验证。','traits':[{'title':'先核对证据，再形成承诺','description':'可能更关注结论的验证依据，倾向追问尚未闭环的条件。','evidence':[q]}],'likelyLines':[{'text':'先把还没有验证的条件说清楚，再讨论能承诺到什么范围。','basis':[q]}]}
 elif '工作区自由输入助手' in prompt:
  CALLS.append('自由输入办理');result={'clarification':'','operations':[{'type':'update_object','objectId':'builtin-project','fields':{'personality':'用户补充观察：更关注风险边界，承诺前倾向核查未验证条件，仍需后续互动验证。'}},{'type':'add_quotes','objectId':'builtin-project','quotes':['先把没验证的条件讲清楚，再谈交付。']},{'type':'intensity','value':'深入'}]}
 elif '长期沟通画像' in prompt:
  CALLS.append('长期沟通画像');result=portrait_fixture(source)
 elif '分析完整记录' in prompt:
  CALLS.append('六维与逐轮复盘');result=review_fixture(source)
 else:
  CALLS.append('连续对话');result=dialogue_fixture(messages)
 return validator(result) if validator else result

with tempfile.TemporaryDirectory() as data:
 server.DATA_ROOT=data;server.CONFIG_PATH=str(pathlib.Path(data)/'user_data/apiconfig.json')
 w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server);w.ask=fixture_ask
 w.atomic_config({'apis':[{'id':'authoring-only','name':'界面演示 · 本机替身','baseURL':'http://127.0.0.1:9/v1','apiKey':'','model':'presentation-fixture','useLLM':True}],'active':'authoring-only'})
 http=server.http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);threading.Thread(target=http.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{http.server_port}'
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True)
   page=browser.new_page(viewport={'width':1180,'height':900},device_scale_factor=2);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(url);page.wait_for_function('ws!==null')
   def capture(name,selector,maxheight=None):
    loc=page.locator(selector).first;loc.scroll_into_view_if_needed();loc.evaluate("e=>e.scrollIntoView({block:'start'})");page.wait_for_timeout(120)
    if maxheight:
     b=loc.bounding_box();page.screenshot(path=str(OUT/name),clip={'x':b['x'],'y':max(0,b['y']),'width':b['width'],'height':min(b['height'],maxheight)})
    else:loc.screenshot(path=str(OUT/name))
   capture('nav-practice.png','#workspace')
   for tab in ['objects','experiences','portrait','history']:
    page.click(f'[data-tab={tab}]');capture('nav-'+tab+'.png','#workspace')
   page.click('[data-tab=practice]')
   capture('workspace-overview.png','#workspace',70)
   page.locator('#workspace').evaluate("e=>e.scrollIntoView({block:'start'})");a=page.locator('#workspace').bounding_box();b=page.locator('.setup .section-heading').first.bounding_box();page.screenshot(path=str(OUT/'workspace-overview.png'),clip={'x':a['x'],'y':max(0,a['y']),'width':a['width'],'height':b['y']+b['height']-a['y']+18})
   page.screenshot(path=str(OUT/'home.png'),clip={'x':30,'y':0,'width':1120,'height':835})
   # Import through the real meeting UI, including original-evidence validation and persistence.
   page.fill('#meetingTitle','A项目周例会 · 虚构演示');page.fill('#meetingText',MINUTES);capture('meeting-input.png','#meetingForm')
   page.click('#meetingAnalyze');expect(page.locator('#meetingStatus')).to_contain_text('提取结果已保留')
   page.locator('.meeting-evidence').first.evaluate('(e)=>e.open=true');capture('meeting-preview.png','.meeting-group',page.locator('#meetingPreview .meeting-item').first.evaluate("e=>e.getBoundingClientRect().bottom-document.querySelector('#meetingPreview .meeting-group').getBoundingClientRect().top+12"))
   page.click('#meetingApply');expect(page.locator('#meetingApplyStatus')).to_contain_text('已保存 4 项')
   page.locator('#projectCards details').first.evaluate('(e)=>e.open=true');capture('project-background.png','#projectCards')
   # Training configuration and live send/review are real product actions against this fixture.
   page.select_option('#projectSelect',index=1);page.fill('#goal','明确验证边界与可交付范围，并提出台架优先级的决策请求。');capture('training-setup.png','.setup',page.locator('#goal').evaluate("e=>e.parentElement.getBoundingClientRect().bottom-document.querySelector('.setup').getBoundingClientRect().top+20"))
   page.locator('#projectSelect').evaluate("e=>e.parentElement.scrollIntoView({block:'start'})");a=page.locator('#projectSelect').locator('..').bounding_box();b=page.locator('#background').locator('..').bounding_box();page.screenshot(path=str(OUT/'project-context.png'),clip={'x':a['x'],'y':max(0,a['y']),'width':a['width'],'height':b['y']+b['height']-a['y']});page.click('[data-tab=objects]');capture('objects.png','#objects',page.locator('#objects .object-card').first.evaluate("e=>e.getBoundingClientRect().bottom-document.getElementById('objects').getBoundingClientRect().top+25"))
   page.locator('#workspace').evaluate("e=>e.scrollIntoView({block:'start'})");a=page.locator('#workspace').bounding_box();b=page.locator('#objects .object-card').first.bounding_box();page.screenshot(path=str(OUT/'objects-with-tabs.png'),clip={'x':a['x'],'y':max(0,a['y']),'width':a['width'],'height':b['y']+b['height']-a['y']+18})
   page.click('[data-object-quotes=builtin-project]');page.fill('#objectQuotes','没有验证记录，先不要承诺交付。\n先把测试条件和边界说清楚。');page.click('#quotesAnalyze');expect(page.locator('#quotesStatus')).to_contain_text('语录与 AI 分析已保存');capture('quote-analysis.png','#quoteAnalysis')
   page.click('[data-close=quotesDialog]');page.click('[data-tab=practice]');page.click('#start');expect(page.locator('#chat .bubble')).to_have_count(1)
   page.fill('#reply','基本都差不多了，大家最近一直在加班。周五交付应该没问题。');page.click('#send');expect(page.locator('#chat .bubble')).to_have_count(3)
   capture('conversation.png','#chat')
   first=page.locator('#chat .bubble').first;first.locator('details').evaluate('(e)=>e.open=true');capture('three-level.png','#chat .bubble');first.locator('details').evaluate('(e)=>e.open=false')
   page.fill('#reply','常温验证已通过，高温验证还没有闭环。我负责补齐验证计划，请您帮我确认台架优先级，再确定可交付范围。');page.click('#send');expect(page.locator('#chat .bubble')).to_have_count(5)
   for reply in TRAININGS[0]['replies'][2:]:
    previous=page.locator('#chat .bubble').count();page.fill('#reply',reply);page.click('#send');expect(page.locator('#chat .bubble')).to_have_count(previous+2)
   page.click('#end');expect(page.locator('.bigscore')).to_be_visible();expect(page.locator('#portraitContent')).to_contain_text('主动接住责任')
   capture('review-focus.png','.review-focus');capture('review-radar-chart.png','.radar-layout > div');capture('review-score-lines.png','.dimension-meters')
   primary=page.evaluate('session');(OUT/'primary-review.json').write_text(json.dumps(primary,ensure_ascii=False,indent=2)+'\n')
   page.locator('.round').last.evaluate('(e)=>e.open=true');capture('round-review-last.png','.round:last-child')
   capture('review-summary.png','.review-head');capture('review-radar.png','.radar-section')
   capture('round-review.png','.round');capture('next-actions.png','.next-list');capture('export-actions.png','#sessionActions')
   with page.expect_download() as exported:page.click('#exportHTML')
   assert exported.value.suggested_filename.endswith('.html')
   # Complete two additional six-turn sessions through real UI actions.
   for plan in TRAININGS[1:]:
    page.click('#back');page.click('[data-category='+('technical' if plan['scene']=='anomaly' else 'report')+']')
    page.click('[data-scene='+plan['scene']+']');page.select_option('#objectSelect','builtin-project');page.fill('#goal',plan['goal']);page.click('#start');expect(page.locator('#chat .bubble')).to_have_count(1)
    for i,reply in enumerate(plan['replies']):
     page.fill('#reply',reply);page.click('#send');expect(page.locator('#chat .bubble')).to_have_count(3+2*i)
    page.click('#end');expect(page.locator('.bigscore')).to_be_visible();expect(page.locator('#portraitRetry')).to_be_enabled()
   page.click('[data-tab=portrait]');expect(page.locator('.portrait-summary')).to_contain_text('3 场训练 · 18 条回应')
   page.set_viewport_size({'width':900,'height':1000})
   capture('portrait-summary.png','.portrait-summary')
   for index,key in enumerate(['traits','strengths','directions']):
    loc=page.locator('#portraitContent .portrait-section').nth(index);capture('portrait-'+key+'.png','#portraitContent .portrait-section:nth-of-type('+str(index+1)+')');capture('portrait-'+key+'-first.png','#portraitContent .portrait-section:nth-of-type('+str(index+1)+') .observation')
   first=page.locator('#portraitContent .observation').first;first.locator('details').evaluate('(e)=>e.open=true');capture('portrait-evidence.png','#portraitContent .observation')
   for index in range(3):
    quote=first.locator('blockquote').nth(index);button=first.locator('[data-open-session]').nth(index);quote.scroll_into_view_if_needed();quote.evaluate("e=>e.scrollIntoView({block:'start'})")
    a=quote.bounding_box();b=button.bounding_box();frame=first.bounding_box()
    page.screenshot(path=str(OUT/f'portrait-source-{index+1}.png'),clip={'x':frame['x'],'y':a['y'],'width':frame['width'],'height':b['y']+b['height']-a['y']+6})
   # A second evidence item from a different section stays separate for readable slides.
   page.locator('#portraitContent .portrait-section').nth(2).locator('.observation details').first.evaluate('(e)=>e.open=true')
   capture('portrait-practice.png','#portraitContent .portrait-section:nth-of-type(3) .observation')
   portrait=page.evaluate('ws.portrait');assert portrait['sessionCount']==3 and portrait['sampleCount']==18
   assert len(set(e['sessionId'] for t in portrait['traits'] for e in t['evidence']))==3
   (OUT/'portrait-data.json').write_text(json.dumps(portrait,ensure_ascii=False,indent=2)+'\n')
   first.locator('[data-open-session]').first.click();expect(page.locator('.bigscore')).to_be_visible()
   page.click('[data-tab=portrait]');expect(page.locator('.portrait-summary')).to_contain_text('18 条回应')
   page.set_viewport_size({'width':1180,'height':900})
   page.click('[data-tab=experiences]');page.fill('#experienceSearch','交付');capture('experience-library.png','#experiences',page.locator('#experienceCards .experience-card').first.evaluate("e=>e.getBoundingClientRect().bottom-document.getElementById('experiences').getBoundingClientRect().top+22"));page.fill('#experienceSearch','先明确验证边界');page.locator('.experience-card details').first.evaluate('(e)=>e.open=true');capture('experience-source.png','.experience-card')
   page.click('[data-tab=practice]');page.fill('#freeInput','我觉得朱总更重视风险边界。他今天说：“先把没验证的条件讲清楚，再谈交付。”请补充到画像和语录，并把追问强度调为深入。');capture('free-input-command.png','#freeInput');page.click('#freeSubmit');expect(page.locator('#freeResult')).to_contain_text('补充语录');capture('free-input-result.png','#freeWorkspace');capture('free-saved-result.png','#freeResult')
   page.click('[data-tab=history]');capture('history.png','#history')
   page.evaluate('backToSelection()')
   for theme in ['corporate','forest','ocean','violet']:
    page.evaluate('(t)=>window.CoachTheme.set(t)',theme);page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/f'theme-{theme}.png'),clip={'x':30,'y':0,'width':1120,'height':740})
   assert not errors,errors
   browser.close()
  manifest={'source':'Actual v5.0.17 UI; three six-turn training sessions, native navigation, isolated authoring fixtures','fictional':True,'realModelTested':False,'defaultKeyLoaded':False,'workflows':CALLS,'sessionCount':3,'userReplies':18,'evidenceSourceOpenVerified':True,'images':sorted(p.name for p in OUT.glob('*.png'))}
  (OUT/'capture-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
  print('PASS:',len(manifest['images']),'screenshots;',len(CALLS),'validated fixture calls; real UI actions and HTML export; no page errors or real model/key usage.')
 finally:http.shutdown();http.server_close()
