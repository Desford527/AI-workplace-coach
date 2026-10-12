"""Verify shipped defaults against fresh and legacy installs without model calls."""
import json
import os
import pathlib
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(__file__).resolve().parents[1]
seed=json.loads((ROOT/'default-api.json').read_text())
for case in ('fresh','legacy'):
    with tempfile.TemporaryDirectory() as folder:
        data=pathlib.Path(folder)/'user_data';data.mkdir()
        if case=='legacy':
            (data/'apiconfig.json').write_text(json.dumps({'apis':[{'id':'old-cbx','name':'deepseek-cbx','baseURL':'https://api.deepseek.com','apiKey':'old-test-value','model':'deepseek-v4-flash','reviewModel':'deepseek-v4-flash','useLLM':True},{'id':'other','name':'old-other'}],'active':'old-cbx'}))
        with socket.socket() as probe:
            probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
        env={**os.environ,'COACH_DATA_ROOT':folder,'AHC_NO_OPEN':'1'};env.pop('COACH_DISABLE_BUNDLED_DEFAULTS',None)
        process=subprocess.Popen([sys.executable,'server.py',str(port)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            url='http://127.0.0.1:'+str(port)
            for _ in range(100):
                try:
                    with urllib.request.urlopen(url+'/api/workplace/workspace') as r:ws=json.load(r)
                    break
                except Exception:time.sleep(.1)
            else:raise RuntimeError('Could not start bundled release')
            assert ws.get('release')=='5.0.5'
            cfg=json.loads((data/'apiconfig.json').read_text());assert len(cfg['apis'])==1
            assert {k:v for k,v in cfg['apis'][0].items() if k!='id'}==seed['api'],'Saved default differs from authorized bundle'
            if case=='legacy':assert cfg['active']=='old-cbx'
            with sync_playwright() as pw:
                b=pw.chromium.launch(executable_path=os.environ.get('COACH_CHROMIUM','/usr/bin/chromium'),headless=True)
                page=b.new_page();page.add_init_script("localStorage.setItem('ahc_api_cfg_v1',JSON.stringify({apis:[{id:'browser-old',name:'deepseek-cbx',model:'deepseek-v4-flash',apiKey:'old-browser-test-key'}],active:'browser-old'}))")
                page.goto(url);page.click('#apiOpen');expect(page.locator('#apiName')).to_have_value('DeepSeek527');expect(page.locator('#apiURL')).to_have_value('https://api.deepseek.com');expect(page.locator('#apiModel')).to_have_value('deepseek-flash');expect(page.locator('#apiSelect option')).to_have_count(2);expect(page.locator('#apiKey')).to_have_value('');assert page.locator('#apiKey').get_attribute('placeholder').startswith('已有密钥');assert page.locator('#apiReplaceDefault').count()==0
                assert not page.locator('#apiSelect').inner_text().find('deepseek-cbx')>=0
                page.reload();page.click('#apiOpen');expect(page.locator('#apiName')).to_have_value('DeepSeek527');b.close()
            print('PASS:',case,'startup replaces old defaults automatically, exact bundled key matches, cached browser defaults ignored; no model requests made.')
        finally:
            process.terminate();process.wait(timeout=10)
