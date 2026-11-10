from pathlib import Path
import urllib.request,urllib.error
from playwright.sync_api import sync_playwright
OUT=Path(__file__).resolve().parent/'assets-v15'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True)
 page=b.new_page(viewport={'width':1440,'height':1000},device_scale_factor=2)
 def verified_fetch(route):
  req=route.request
  try:
   with urllib.request.urlopen(urllib.request.Request(req.url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as r:
    route.fulfill(status=r.status,body=r.read(),headers={'content-type':r.headers.get('content-type','application/octet-stream'),'access-control-allow-origin':'*'})
  except Exception:
   route.abort()
 page.route('https://**/*',verified_fetch)
 page.goto('https://github.com/Desford527/AI-workplace-coach',wait_until='domcontentloaded',timeout=60000)
 page.wait_for_timeout(2500)
 print('Stylesheets:',page.evaluate('document.styleSheets.length'))
 print(page.title());page.screenshot(path=str(OUT/'github-repository.png'))
 (OUT/'github-capture.txt').write_text('URL: '+page.url+'\nTitle: '+page.title()+'\nAnonymous public access: HTTP page loaded\n')
 b.close()
