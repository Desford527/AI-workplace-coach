"""Chromium acceptance for free input/library using an explicit local model double."""
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
from fake_provider import start,Provider
ROOT=pathlib.Path(__file__).resolve().parents[1]
ART=pathlib.Path('/tmp/workplace-browser-artifacts');ART.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as data:
    mock=start()
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    env={**os.environ,'COACH_DATA_ROOT':data,'AHC_NO_OPEN':'1','COACH_DISABLE_BUNDLED_DEFAULTS':'1'}
    proc=subprocess.Popen([sys.executable,'server.py',str(port)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    url=f'http://127.0.0.1:{port}'
    try:
        for _ in range(80):
            try:urllib.request.urlopen(url+'/api/workplace/workspace').close();break
            except Exception:time.sleep(.1)
        else:raise RuntimeError('Local server failed to start')
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True)
            page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(url)
            # Without a configured model, keep the input and all original objects.
            page.fill('#freeInput','我想新增一个对象，王工是测试负责人');page.click('#freeSubmit')
            expect(page.locator('#freeStatus')).to_contain_text('未保存修改')
            expect(page.locator('#freeInput')).to_have_value('我想新增一个对象，王工是测试负责人')
            page.click('#apiOpen');page.fill('#apiName','自由输入验收 · 测试替身');page.fill('#apiURL',f'http://127.0.0.1:{mock.server_port}/v1');page.fill('#apiModel','dialog-model');page.fill('#apiReviewModel','review-model');page.click('#apiForm button[type=submit]');expect(page.locator('#apiStatus')).to_contain_text('已保存');page.click('[data-close=apiDialog]')
            page.click('#freeSubmit');expect(page.locator('#freeResult')).to_contain_text('新建对象：王工')
            page.click('[data-tab=objects]');expect(page.locator('#objectCards .object-card')).to_have_count(5)
            page.fill('#freeInput','模糊对象，更重视验证');page.click('#freeSubmit');expect(page.locator('#freeResult')).to_contain_text('还需要确认一点')
            page.fill('#freeInput','是朱总');page.click('#freeSubmit');expect(page.locator('#freeResult')).to_contain_text('补充画像：朱总')
            page.click('[data-tab=practice]');page.select_option('#objectSelect','builtin-project');page.click('#start');expect(page.locator('#sessionTitle')).to_contain_text('朱总')
            page.fill('#freeInput','我觉得朱总重视风险，今天说：“先把没验证的条件讲清楚，再谈交付。”增加追问强度；收录一条汇报延期的经验。');page.click('#freeSubmit');expect(page.locator('#freeResult')).to_contain_text('补充语录')
            expect(page.locator('#sessionMeta')).to_contain_text('深入追问');expect(page.locator('#intensity')).to_have_value('深入')
            page.click('[data-tab=experiences]');expect(page.locator('.experience-card')).to_have_count(9)
            page.screenshot(path=str(ART/'v5.0.13-experience-desktop.png'),full_page=True)
            page.click('#newExperience');page.fill('#experienceName','人工录入示例');page.fill('#experienceContent','先确认问题，再回答。');page.click('#experienceForm button[type=submit]');expect(page.locator('#experienceDialog')).not_to_be_visible();expect(page.locator('.experience-card')).to_have_count(10)
            page.locator('#experienceFile').set_input_files({'name':'经验导入.md','mimeType':'text/markdown','buffer':'向上汇报要说明风险、责任人与下一步。'.encode()});expect(page.locator('.experience-card')).to_have_count(11)
            batch=[{'title':'JSON 导入示例','category':'技术评审','content':'给出测试条件与判据。'}]
            page.locator('#experienceFile').set_input_files({'name':'经验.json','mimeType':'application/json','buffer':json.dumps(batch).encode()});expect(page.locator('.experience-card')).to_have_count(12)
            page.fill('#experienceSearch','JSON 导入示例');expect(page.locator('.experience-card')).to_have_count(1);page.fill('#experienceSearch','')
            with page.expect_download() as dl:page.click('#exportExperiences')
            exported=json.loads(pathlib.Path(dl.value.path()).read_text());assert len(exported)==12
            # Error does not clear the user's text or create a phantom result.
            Provider.mode='payment';page.fill('#freeInput','增加追问强度');page.click('#freeSubmit');expect(page.locator('#freeStatus')).to_contain_text('402');expect(page.locator('#freeInput')).to_have_value('增加追问强度');Provider.mode='ok'
            page.reload();expect(page.locator('#sessionMeta')).to_contain_text('深入追问');page.click('[data-tab=experiences]');expect(page.locator('.experience-card')).to_have_count(12);expect(page.locator('#freeHistory')).to_contain_text('补充语录')
            for theme in ('corporate','forest','ocean','violet'):
                page.evaluate('(theme)=>window.CoachTheme.set(theme)',theme)
                page.set_viewport_size({'width':390,'height':844})
                page.locator('#freeWorkspace').scroll_into_view_if_needed();page.screenshot(path=str(ART/f'v5.0.13-{theme}-free-mobile.png'))
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),theme
            page.evaluate("window.CoachTheme.set('corporate')");page.set_viewport_size({'width':1440,'height':1000})
            page.locator('#freeWorkspace').scroll_into_view_if_needed();page.screenshot(path=str(ART/'v5.0.13-free-desktop.png'))
            assert not errors,errors
            browser.close()
        print('PASS: free create/update/quotes/intensity, clarification, library forms/TXT-Markdown/JSON/export, persistence, HTTP 402 input retention, four mobile themes; explicit local model double.')
    finally:
        proc.terminate();proc.wait(timeout=10);mock.shutdown();mock.server_close()
