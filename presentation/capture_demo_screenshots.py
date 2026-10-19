"""Authoring utility: capture real UI using fictional display data; no model or real API key. Requires Playwright/Chromium, not used by the application."""
import json,os,pathlib,socket,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1];APP=ROOT/'workplace-v5';OUT=ROOT/'presentation/assets'
with tempfile.TemporaryDirectory() as data:
 with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 proc=subprocess.Popen([sys.executable,'server.py',str(port)],cwd=APP,env={**os.environ,'COACH_DATA_ROOT':data,'COACH_DISABLE_BUNDLED_DEFAULTS':'1','AHC_NO_OPEN':'1'},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 url=f'http://127.0.0.1:{port}'
 try:
  for _ in range(80):
   try:urllib.request.urlopen(url+'/api/workplace/workspace').close();break
   except Exception:time.sleep(.1)
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True)
   page=browser.new_page(viewport={'width':1440,'height':1040},device_scale_factor=1.5)
   page.goto(url);page.wait_for_function('ws!==null')
   page.evaluate("$('apiBadge').textContent='界面演示'")
   page.screenshot(path=str(OUT/'home.png'),clip={'x':60,'y':10,'width':1320,'height':820})
   workspace=json.load(urllib.request.urlopen(url+'/api/workplace/workspace'))
   scene=next(s for s in workspace['scenes'] if s['id']=='progress');obj=next(o for o in workspace['objects'] if o['id']=='builtin-project')
   messages=[{'id':'d1','role':'assistant','text':'先说你的判断：能否按计划交付？今天需要我协调或决定什么？','interpretation':{'surface':'询问交付判断和待协调事项。','real':'模拟解读：需要以明确判断和证据支持决策。','hidden':'模拟解读：关注责任、风险边界及下一步。'}}, {'id':'d2','role':'user','text':'基本都差不多了，大家最近一直在加班。周五交付应该没问题。'}, {'id':'d3','role':'assistant','text':'加班我记下了，但不能当作交付依据。哪些验证已经关闭，哪些还没关闭？周五交付的具体范围是什么？','interpretation':{'surface':'追问验证状态和交付范围。','real':'模拟解读：希望把态度表述转成可核实的交付依据。','hidden':'模拟解读：避免未经验证的承诺，明确可交付范围。'}}]
   sample={'id':'presentation-fictional','at':'2026-10-19T12:00:00Z','scene':scene,'object':obj,'goal':'用事实支持交付判断，并提出具体决策请求。','background':'虚构演示场景：周五交付前的验证状态汇报。','intensity':'标准','apiId':'presentation-only','messages':messages,'status':'active','revision':1,'experiences':[],'project':None}
   page.evaluate('s=>applySession(s)',sample);page.locator('#sessionPanel').scroll_into_view_if_needed();page.locator('#useCurrentAPI').evaluate('(e)=>e.hidden=true');page.locator('#sessionError').evaluate('(e)=>e.hidden=true')
   page.locator('#chat').evaluate("e=>{e.style.maxHeight='none';e.style.height='auto';e.style.overflow='visible';e.scrollTop=0;}");page.locator('#chat').screenshot(path=str(OUT/'conversation-full.png'))
   # Product controls are unmodified; only the display data above is fictional.
   page.evaluate('backToSelection()');page.locator('#meetings').scroll_into_view_if_needed()
   page.fill('#meetingTitle','项目周例会 · 演示样例');page.fill('#meetingText','朱总：“没有验证记录，先不要承诺交付。”\n项目现状：高温验证尚未完成。\n行动项：王工补齐验证记录，再确认可交付范围。\n沟通经验：先讲未验证项，再提出决策请求。')
   page.locator('#meetings > .panel').first.screenshot(path=str(OUT/'meeting.png'))
   page.fill('#freeInput','我觉得朱总更重视风险边界。他今天说：“先把没验证的条件讲清楚，再谈交付。”请补充到画像和语录，追问强度调为深入。')
   page.locator('#freeWorkspace').screenshot(path=str(OUT/'free-input.png'))
   page.screenshot(path='/tmp/coach-presentation/layout-bottom.png',full_page=True)
   assert page.evaluate("$('meetings').nextElementSibling.id==='freeWorkspace'")
   browser.close()
  print('Captured real application layouts. Conversation data is explicitly fictional for presentation; no model request or key used.')
 finally:proc.terminate();proc.wait(timeout=10)
