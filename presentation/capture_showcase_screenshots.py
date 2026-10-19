"""Capture actual product workflows with isolated, deterministic authoring fixtures.
Only this authoring process replaces ask(); application source/default Key stay unchanged.
All sample texts and scores are fictional, not real-model or business-effect evidence.
"""
import copy,json,os,pathlib,socket,sys,tempfile,threading,time,urllib.request
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(__file__).resolve().parents[1];APP=ROOT/'workplace-v5';OUT=ROOT/'presentation/assets-v2';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(APP));sys.argv=[sys.argv[0]]
os.environ['COACH_DISABLE_BUNDLED_DEFAULTS']='1'
import server
import workplace as w
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
  CALLS.append('长期沟通画像');data=json.loads(source);s=data['sessions'][0];users=[m for m in s['messages'] if m['role']=='user'];m=users[-1]
  ev=[{'sessionId':s['id'],'messageId':m['id'],'quote':m['text']}]
  result={'summary':'目前依据少量练习，已开始用验证状态和责任安排支持判断；决策请求仍可更具体。此为初步观察。','traits':[{'title':'开始区分事实与判断','description':'后续回答主动说明验证状态，并保留暂时无法承诺的边界。','evidence':ev}],'strengths':[{'title':'愿意补充责任人与下一步','description':'能提出由自己补齐验证计划，表达了推进问题的意愿。','evidence':ev}],'directions':[{'title':'让资源请求可以直接决定','description':'请求需要进一步明确优先级、截止时间与备选安排。','action':'下次用一句话说清：请对方决定什么、最晚何时决定。','evidence':ev}]}
 elif '分析完整记录' in prompt:
  CALLS.append('六维与逐轮复盘');msgs=json.loads(source);users=[m for m in msgs if m['role']=='user'];bots=[m for m in msgs if m['role']=='assistant']
  def dims(m,values):return [{'name':name,'score':value,'basis':basis,'evidence':[{'messageId':m['id'],'quote':m['text']}]} for name,value,basis in zip(DIMS,values,['给出了方向，但交付范围仍可明确。','验证状态比态度更有助于核查。','请求还需要明确优先级与时间。','说明未验证项，避免无条件承诺。','提供责任安排，并可补充反馈时间。','愿意回应当前问题并推进协作。'])]
  result={'summary':'开始补充验证边界与责任安排，下一步把决策请求说具体。','overall':'第一轮用“差不多”和加班说明状态，尚不能支持交付决策。第二轮开始区分验证状态与交付承诺，也提出了责任安排。继续练习时，建议明确可交付范围、需要对方确认的台架优先级和反馈时间。','sampleLimit':'仅依据本次两轮演示回应，供界面展示，不代表真实模型评价。','dims':dims(users[-1],[62,48,51,56,70,68]),'timeline':[{'messageId':m['id'],'dims':dims(m,[35,25,30,28,45,52] if i==0 else [62,58,54,68,72,70]),'feedback':'本轮态度积极，但还需要用验证状态支持判断，并明确需要对方决定的事项。' if i==0 else '已说明验证边界与责任安排；可以进一步给出同步时间和明确的决策请求。','improved':'当前还不能承诺完整交付。我会先核实[未关闭验证项]并在[时间]同步；请您确认[台架优先级]，再决定可交付范围。'} for i,m in enumerate(users)],'translations':[{'messageId':m['id'],**m['interpretation']} for m in bots], 'loss':[{'title':'用态度代替验证证据','desc':'“一直加班”说明投入，仍无法说明交付条件是否满足。','action':'把已完成项、未关闭项和待确认信息分开说。'},{'title':'把协调请求落成具体决定','desc':'需要让对方清楚当前要决定什么。','action':'明确台架优先级、决定时间和备选安排。'}],'next':['开场先给一句有边界的判断。','只使用核实过的验证状态支持结论。','用一句话说明请求、责任人与时间。'],'language':'使用短句，先回答当前问题。'}
 else:
  CALLS.append('连续对话');count=sum(m['role']=='user' and not m['content'].startswith('请按上述工作场景') for m in messages)
  line=['我们用几分钟对齐交付状态。先说你的判断：能否按计划交付？今天需要我决定什么？','加班我记下了，但不能当作交付依据。哪些验证已经关闭，哪些还没关闭？周五要交付的具体范围是什么？','那就把未验证项和台架需求列清楚。你希望我今天决定哪个优先级？补齐后什么时间再同步？'][min(count,2)]
  result={'line':line,'surface':'确认验证状态、交付范围和需要协调的事项。','real':'希望用可核查的事实支持交付判断，并明确当前决策。','hidden':'模拟解读：关注承诺边界、责任分工和下一次同步安排。'}
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
   page.click('[data-object-quotes=builtin-project]');page.fill('#objectQuotes','没有验证记录，先不要承诺交付。\n先把测试条件和边界说清楚。');page.click('#quotesAnalyze');expect(page.locator('#quotesStatus')).to_contain_text('语录与 AI 分析已保存');capture('quote-analysis.png','#quoteAnalysis')
   page.click('[data-close=quotesDialog]');page.click('[data-tab=practice]');page.click('#start');expect(page.locator('#chat .bubble')).to_have_count(1)
   page.fill('#reply','基本都差不多了，大家最近一直在加班。周五交付应该没问题。');page.click('#send');expect(page.locator('#chat .bubble')).to_have_count(3)
   capture('conversation.png','#chat')
   first=page.locator('#chat .bubble').first;first.locator('details').evaluate('(e)=>e.open=true');capture('three-level.png','#chat .bubble');first.locator('details').evaluate('(e)=>e.open=false')
   page.fill('#reply','常温验证已通过，高温验证还没有闭环。我负责补齐验证计划，请您帮我确认台架优先级，再确定可交付范围。');page.click('#send');expect(page.locator('#chat .bubble')).to_have_count(5)
   page.click('#end');expect(page.locator('.bigscore')).to_be_visible();expect(page.locator('#portraitContent')).to_contain_text('初步观察')
   capture('review-summary.png','.review-head');capture('review-radar.png','.radar-section')
   capture('round-review.png','.round');capture('next-actions.png','.next-list');capture('export-actions.png','#sessionActions')
   with page.expect_download() as exported:page.click('#exportHTML')
   assert exported.value.suggested_filename.endswith('.html')
   page.click('[data-tab=portrait]');page.locator('#portraitContent .observation details').first.evaluate('(e)=>e.open=true');capture('personal-portrait.png','#portrait',page.locator('#portraitContent .portrait-section').first.evaluate("e=>e.getBoundingClientRect().bottom-document.getElementById('portrait').getBoundingClientRect().top+22"));capture('portrait-summary.png','.portrait-summary');capture('portrait-evidence.png','#portraitContent .observation')
   page.click('[data-tab=experiences]');page.fill('#experienceSearch','交付');capture('experience-library.png','#experiences',page.locator('#experienceCards .experience-card').first.evaluate("e=>e.getBoundingClientRect().bottom-document.getElementById('experiences').getBoundingClientRect().top+22"));page.fill('#experienceSearch','先明确验证边界');page.locator('.experience-card details').first.evaluate('(e)=>e.open=true');capture('experience-source.png','.experience-card')
   page.fill('#freeInput','我觉得朱总更重视风险边界。他今天说：“先把没验证的条件讲清楚，再谈交付。”请补充到画像和语录，并把追问强度调为深入。');capture('free-input-command.png','#freeInput');page.click('#freeSubmit');expect(page.locator('#freeResult')).to_contain_text('补充语录');capture('free-input-result.png','#freeWorkspace');capture('free-saved-result.png','#freeResult')
   page.click('[data-tab=history]');capture('history.png','#history')
   page.evaluate('backToSelection()')
   for theme in ['corporate','forest','ocean','violet']:
    page.evaluate('(t)=>window.CoachTheme.set(t)',theme);page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/f'theme-{theme}.png'),clip={'x':30,'y':0,'width':1120,'height':740})
   assert not errors,errors
   browser.close()
  manifest={'source':'Actual v5.0.15 UI in Chromium, isolated local data, validated authoring fixtures','fictional':True,'realModelTested':False,'defaultKeyLoaded':False,'workflows':CALLS,'images':sorted(p.name for p in OUT.glob('*.png'))}
  (OUT/'capture-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
  print('PASS:',len(manifest['images']),'screenshots;',len(CALLS),'validated fixture calls; real UI actions and HTML export; no page errors or real model/key usage.')
 finally:http.shutdown();http.server_close()
