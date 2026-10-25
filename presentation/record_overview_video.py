"""Record the real local UI with isolated fictional data; no production model or Key."""
import json,os,pathlib,subprocess,sys,tempfile,threading,time
from playwright.sync_api import sync_playwright,expect

ROOT=pathlib.Path(__file__).resolve().parents[1];APP=ROOT/'workplace-v5';OUT=ROOT/'presentation/video-v7';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(APP));sys.argv=[sys.argv[0]]
os.environ['COACH_DISABLE_BUNDLED_DEFAULTS']='1'
import server
import workplace as w
from story_v4_demo import TRAININGS,dialogue_fixture,review_fixture,portrait_fixture
from story_v5_demo import COMMANDS,free_fixture
CALLS=[]

def fixture(messages,review=False,config=None,validator=None):
 prompt=messages[0]['content'];source=messages[-1]['content']
 if '长期沟通画像' in prompt:kind='画像';result=portrait_fixture(source)
 elif '分析完整记录' in prompt:kind='复盘';result=review_fixture(source)
 elif '工作区自由输入助手' in prompt:kind='自由输入';result=free_fixture(source)
 else:kind='连续对话';result=dialogue_fixture(messages)
 CALLS.append(kind)
 return validator(result) if validator else result

SCENES=[
 ('home',3.5,'AI职场沟通训练师：把下一次高压沟通，提前练一遍。'),
 ('setup',3.5,'选场景、选对象、定目标，让练习贴近实际任务。'),
 ('chat',4,'在连续追问中，练习把判断、依据和请求说清楚。'),
 ('score',2.5,'结束训练，先看总分与本轮反馈。'),
 ('radar',2.5,'再看六维表现，找到下一轮最值得改的一点。'),
 ('objects',3,'对象画像：维护关注点、沟通习惯和语录。'),
 ('portrait',3.5,'我的沟通画像：从多轮原话中积累观察与练习方向。'),
 ('experience',3.5,'沟通经验库：导入、检索，让好方法继续复用。'),
 ('meeting',3.5,'导入会议纪要，为对象、项目和经验补充真实资料。'),
 ('direct',4,'想改什么，直接说：一句话新增一个沟通对象。'),
 ('result',2,'王工已进入对象画像，保存效果可以直接看到。'),
 ('ending',3,'接下来，从一次常见的交付汇报说起。'),
]
MINUTES='【虚构演示】A项目周例会\n朱总：没有验证记录，先不要承诺交付。\n当前状态：高温验证尚未闭环。\n行动项：王工补齐验证记录，下次周会确认交付边界。'

def ffprobe(path):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],text=True))

def ass_time(s):
 cs=round(s*100);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);sec,cs=divmod(cs,100)
 return f'{h}:{m:02d}:{sec:02d}.{cs:02d}'

def srt_time(s):
 ms=round(s*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);sec,ms=divmod(ms,1000)
 return f'{h:02d}:{m:02d}:{sec:02d},{ms:03d}'

with tempfile.TemporaryDirectory(prefix='coach-video-') as tmp:
 server.DATA_ROOT=tmp;server.CONFIG_PATH=str(pathlib.Path(tmp)/'user_data/apiconfig.json')
 w.init(server.ROOT,tmp,server.CONFIG_PATH,server);w.ask=fixture
 w.atomic_config({'apis':[{'id':'video-only','name':'DeepSeek527 · 视频演示','baseURL':'http://127.0.0.1:9/v1','apiKey':'','model':'video-fixture','useLLM':True}],'active':'video-only'})
 http=server.http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);threading.Thread(target=http.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{http.server_port}'
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True)
   prep=browser.new_context(viewport={'width':1280,'height':720},timezone_id='Asia/Shanghai',locale='zh-CN');page=prep.new_page();page.goto(url);page.wait_for_function('ws!==null');ids=[]
   # Prepare real validated histories before the recording starts.
   for i,plan in enumerate(TRAININGS):
    if i:page.click('#back')
    page.click('[data-category='+('technical' if plan['scene']=='anomaly' else 'report')+']');page.click('[data-scene='+plan['scene']+']');page.select_option('#objectSelect','builtin-project');page.fill('#goal',plan['goal']);page.click('#start');expect(page.locator('#chat .bubble')).to_have_count(1)
    for n,reply in enumerate(plan['replies']):
     page.fill('#reply',reply);page.click('#send');expect(page.locator('#chat .bubble')).to_have_count(3+2*n)
    page.click('#end');expect(page.locator('.bigscore')).to_be_visible();expect(page.locator('#portraitRetry')).to_be_enabled();ids.append(page.evaluate('session.id'))
   assert page.evaluate('ws.portrait.sessionCount===3&&ws.portrait.sampleCount===18')
   page.click('#back');page.click('[data-category=report]');page.click('[data-scene=progress]');page.click('#start');expect(page.locator('#chat .bubble')).to_have_count(1)
   for n,reply in enumerate(TRAININGS[0]['replies'][:2]):
    page.fill('#reply',reply);page.click('#send');expect(page.locator('#chat .bubble')).to_have_count(3+2*n)
   active_id=page.evaluate('session.id');prep.close()

   context=browser.new_context(viewport={'width':1280,'height':720},record_video_dir=str(pathlib.Path(tmp)/'raw'),record_video_size={'width':1280,'height':720},timezone_id='Asia/Shanghai',locale='zh-CN')
   external=[]
   def local_only(route):
    if route.request.url.startswith(url+'/'):route.continue_()
    else:external.append(route.request.url);route.abort()
   context.route('**/*',local_only)
   origin=time.monotonic();page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);page.wait_for_function('ws!==null');page.wait_for_timeout(600)
   lead=time.monotonic()-origin;begin=time.monotonic();timeline=[]
   def scroll(selector):page.locator(selector).first.evaluate("e=>e.scrollIntoView({block:'start',behavior:'instant'})")
   def tab(name):
    scroll('#workspace');page.click('[data-tab='+name+']');scroll('#workspace')
   start=0
   for key,duration,caption in SCENES:
    deadline=begin+start+duration
    if key=='home':page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    elif key=='setup':
     tab('practice');page.wait_for_timeout(1250);scroll('.setup')
    elif key=='chat':
     page.evaluate('(id)=>openSession(id)',active_id);expect(page.locator('#chat .bubble')).to_have_count(5);scroll('#workspace');page.locator('#chat').evaluate('(e)=>e.scrollTop=0')
    elif key=='score':
     page.evaluate('(id)=>openSession(id)',ids[0]);expect(page.locator('.bigscore')).to_be_visible();scroll('.review-head')
    elif key=='radar':scroll('.radar-section')
    elif key=='objects':tab('objects')
    elif key=='portrait':tab('portrait')
    elif key=='experience':tab('experiences')
    elif key=='meeting':
     page.fill('#meetingTitle','A项目周例会 · 虚构演示');page.fill('#meetingText',MINUTES);scroll('#meetings')
    elif key=='direct':
     scroll('#freeWorkspace');page.click('#freeInput');page.locator('#freeInput').press_sequentially(COMMANDS['create']['input'],delay=15)
    elif key=='result':
     page.click('#freeSubmit');expect(page.locator('#freeResult')).to_contain_text('新建对象');tab('objects');ident=page.evaluate("ws.objects.find(o=>o.name==='王工').id");page.locator('[data-edit-object="'+ident+'"]').locator('../..').scroll_into_view_if_needed()
    elif key=='ending':page.evaluate("backToSelection();window.scrollTo({top:0,behavior:'instant'})")
    remaining=deadline-time.monotonic()
    assert remaining>-.3,(key,'scene overrun',remaining)
    if remaining>0:page.wait_for_timeout(remaining*1000)
    timeline.append({'scene':key,'start':start,'end':start+duration,'caption':caption});start+=duration
   assert not errors,errors
   assert not external,external
   video=page.video;context.close();raw=pathlib.Path(video.path());browser.close()
  ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 816
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Noto Sans CJK SC,27,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,32,32,0,1
Style: Small,Noto Sans CJK SC,15,&H00F5D6DB,&H00F5D6DB,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,32,32,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
  srt=[]
  for i,row in enumerate(timeline,1):
   ass+=f'Dialogue: 0,{ass_time(row["start"])},{ass_time(row["end"])},Main,,0,0,0,,{{\\pos(32,735)}}{row["caption"]}\n'
   srt.extend([str(i),srt_time(row['start'])+' --> '+srt_time(row['end']),row['caption'],''])
  ass+=f'Dialogue: 1,0:00:00.00,{ass_time(start)},Small,,0,0,0,,{{\\pos(34,784)}}真实页面录屏 · 本机虚构演示数据 · 未展示真实密钥\n'
  (OUT/'overview.ass').write_text(ass);(OUT/'overview.zh-CN.srt').write_text('\n'.join(srt))
  output=OUT/'AI-workplace-coach-overview-v7.mp4'
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-ss',str(lead),'-i',str(raw),'-t',str(start),'-vf',f'pad=1280:816:0:0:color=0xc70019,ass={OUT/"overview.ass"}', '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-r','30','-movflags','+faststart','-an',str(output)],check=True)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss','0.7','-i',str(output),'-frames:v','1',str(OUT/'poster.png')],check=True)
  info=ffprobe(output);stream=info['streams'][0]
  assert stream['codec_name']=='h264' and stream['width']==1280 and stream['height']==816 and stream['pix_fmt']=='yuv420p'
  assert abs(float(info['format']['duration'])-start)<.2
  manifest={'duration':float(info['format']['duration']),'width':1280,'height':816,'codec':'H.264','audio':False,'subtitles':'burned-in Chinese and standalone SRT','source':'Actual v5.0.18 local browser recording, not a screenshot slideshow','realModelTested':False,'defaultKeyLoaded':False,'completedSessions':3,'portraitReplies':18,'validatedFixtureCalls':len(CALLS),'pageErrors':errors,'externalRequests':external,'timezone':'Asia/Shanghai','timeline':timeline}
  (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
  print('PASS: recorded',start,'seconds; H.264 1280x816; live UI; 3 validated reviewed sessions; direct-input object saved; no page errors, external requests, real model or default Key.')
 finally:http.shutdown();http.server_close()
