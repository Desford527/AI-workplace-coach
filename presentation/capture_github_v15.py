"""Capture a clearly labelled reader view from actual public GitHub HTML.
The environment blocks github.githubassets.com; no repository data is invented.
"""
from pathlib import Path
import urllib.request,json
from lxml import html
from playwright.sync_api import sync_playwright
OUT=Path(__file__).resolve().parent/'assets-v15';OUT.mkdir(exist_ok=True)
url='https://github.com/Desford527/AI-workplace-coach'
with urllib.request.urlopen(url,timeout=25) as r:source=r.read();status=r.status
root=html.fromstring(source)
header=root.xpath('//*[@id="repo-title-component"]')[0]
table=root.xpath('//table')[0]
def outer(el):return html.tostring(el,encoding='unicode')
style='''thead th:not(:nth-child(2)){display:none}tbody td:not(.react-directory-row-name-cell-large-screen){display:none}.repo .d-flex{display:flex;align-items:center;gap:12px}body{margin:0;background:#fff;color:#1f2328;font:18px Arial,sans-serif}main{padding:38px 50px}.source{background:#f6f8fa;border-bottom:1px solid #d0d7de;padding:20px 50px;font-size:19px;color:#59636e}.repo{padding:20px 0 30px;font-size:30px}.repo img{display:none}.repo strong{display:inline-block;margin-right:18px}.repo span{font-size:15px;border:1px solid #d0d7de;border-radius:20px;padding:4px 10px}a{color:#0969da;text-decoration:none}table{border-collapse:collapse;width:100%;border:1px solid #d0d7de;border-radius:8px}th,td{text-align:left;padding:17px 22px;border-bottom:1px solid #d8dee4}thead{background:#f6f8fa}th{font-size:16px;color:#59636e}.react-directory-row-name-cell-small-screen{display:none}.react-directory-filename-column{display:flex;align-items:center;gap:14px}.react-directory-row-commit-cell,td:last-child,th:last-child{display:none}svg{color:#54aeff}.sr-only,[class*="VisuallyHidden"],[class*="visuallyHidden"]{display:none}.foot{margin-top:25px;color:#59636e;font-size:17px}'''
doc='<html><meta charset="utf-8"><style>'+style+'</style><div class="source">'+url+'</div><main><div class="repo">'+outer(header)+'</div>'+outer(table)+'<div class="foot">公开仓库实际内容 · 简洁视图</div></main></html>'
(OUT/'github-reader.html').write_text(doc)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True);page=b.new_page(viewport={'width':1720,'height':840},device_scale_factor=2)
 page.route('https://**/*',lambda route:route.abort());page.set_content(doc);page.screenshot(path=str(OUT/'github-styled.png'));b.close()
(OUT/'github-capture.txt').write_text('Source: '+url+'\nHTTP status: '+str(status)+'\nActual public HTML; repository title, Public badge and file table retained. Local reader stylesheet; CDN inaccessible. Not original GitHub CSS.\n')
print('Captured actual repository content in labelled reader view')
