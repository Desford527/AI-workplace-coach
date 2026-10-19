"""Meeting import acceptance in Chromium; explicitly uses a local model double."""
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
from test_meetings import MINUTES,docx_bytes
ROOT=pathlib.Path(__file__).resolve().parents[1]
ART=pathlib.Path('/tmp/workplace-browser-artifacts');ART.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as data:
    mock=start()
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    proc=subprocess.Popen([sys.executable,'server.py',str(port)],cwd=ROOT,env={**os.environ,'COACH_DATA_ROOT':data,'COACH_DISABLE_BUNDLED_DEFAULTS':'1','AHC_NO_OPEN':'1'},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    url=f'http://127.0.0.1:{port}'
    try:
        for _ in range(80):
            try:urllib.request.urlopen(url+'/api/workplace/workspace').close();break
            except Exception:time.sleep(.1)
        else:raise RuntimeError('Server did not start')
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True)
            page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(url);assert page.evaluate("document.getElementById('meetings').nextElementSibling.id==='freeWorkspace'");assert page.locator('[data-tab=meetings]').count()==0;page.locator('#meetings').scroll_into_view_if_needed();expect(page.locator('#meetingForm')).to_be_visible()
            page.locator('#meetingFile').set_input_files({'name':'A项目周例会.docx','mimeType':'application/vnd.openxmlformats-officedocument.wordprocessingml.document','buffer':docx_bytes()})
            expect(page.locator('#meetingStatus')).to_contain_text('已读取正文');expect(page.locator('#meetingText')).to_have_value(MINUTES)
            page.click('#meetingAnalyze');expect(page.locator('#meetingStatus')).to_contain_text('尚未更新资料');expect(page.locator('#meetingText')).to_have_value(MINUTES)
            page.click('#apiOpen');page.fill('#apiName','会议纪要验收 · 测试替身');page.fill('#apiURL',f'http://127.0.0.1:{mock.server_port}/v1');page.fill('#apiModel','dialog-model');page.fill('#apiReviewModel','review-model');page.click('#apiForm button[type=submit]');expect(page.locator('#apiStatus')).to_contain_text('已保存');page.click('[data-close=apiDialog]')
            page.click('#meetingAnalyze');expect(page.locator('#meetingStatus')).to_contain_text('提取结果已保留');expect(page.locator('[data-meeting-item]')).to_have_count(7)
            expect(page.locator('[data-meeting-target="朱总"]')).to_have_value('builtin-project');expect(page.locator('[data-meeting-target="王工"]')).to_have_value('new')
            page.locator('.meeting-evidence').first.evaluate('(el)=>el.open=true');expect(page.locator('.meeting-evidence').first).to_contain_text('朱总要求先核实')
            page.locator('#meetingPreview').screenshot(path=str(ART/'v5.0.15-meeting-preview.png'))
            # Save a subset first, then the rest; creation and repeated save do not duplicate.
            page.locator('[data-meeting-item="4"]').uncheck();page.click('#meetingApply');expect(page.locator('#meetingApplyStatus')).to_contain_text('已保存 6 项')
            expect(page.locator('[data-meeting-item="4"]')).to_be_checked();page.click('#meetingApply');expect(page.locator('#meetingApplyStatus')).to_contain_text('已保存 1 项');expect(page.locator('#meetingApply')).to_be_disabled()
            page.click('[data-tab=objects]');expect(page.locator('#meetings')).to_be_visible();expect(page.locator('.object-card')).to_have_count(5)
            page.click('[data-tab=experiences]');expect(page.locator('.experience-card')).to_have_count(9)
            page.click('[data-tab=practice]');expect(page.locator('#projectSelect option')).to_have_count(2)
            project_id=page.locator('#projectSelect option').nth(1).get_attribute('value');page.select_option('#projectSelect',project_id)
            assert '高温验证' in page.input_value('#background')
            page.fill('#background','仅使用本次编辑后的脱敏背景');page.click('#start');expect(page.locator('#sessionTitle')).to_contain_text('朱总')
            session_id=page.evaluate("localStorage.getItem('workplace_active_session')")
            stored=json.load(urllib.request.urlopen(url+'/api/workplace/session?id='+session_id));assert stored['project']['id']==project_id
            assert stored['background']=='仅使用本次编辑后的脱敏背景'
            page.locator('#meetings').scroll_into_view_if_needed();page.reload();page.locator('#meetings').scroll_into_view_if_needed();expect(page.locator('#meetingRecords')).to_contain_text('已保存 7 项')
            page.locator('#meetingRecords [data-open-meeting]').click();expect(page.locator('#meetingApply')).to_be_disabled()
            # Same source returns the saved preview without another model call.
            count=len(Provider.calls);page.fill('#meetingText',MINUTES);page.fill('#meetingTitle','同一会议另一文件名');page.click('#meetingAnalyze');expect(page.locator('#meetingStatus')).to_contain_text('提取结果已保留');assert len(Provider.calls)==count
            Provider.mode='payment';page.fill('#meetingText',MINUTES+'\n下次会议另行安排。');page.click('#meetingAnalyze');expect(page.locator('#meetingStatus')).to_contain_text('402');expect(page.locator('#meetingText')).to_have_value(MINUTES+'\n下次会议另行安排。');Provider.mode='ok'
            expect(page.locator('#meetingPreview')).not_to_be_visible()
            page.locator('#meetingRecords [data-open-meeting]').click();expect(page.locator('#meetingPreview')).to_be_visible()
            for theme in ('corporate','forest','ocean','violet'):
                page.evaluate('(name)=>window.CoachTheme.set(name)',theme);page.set_viewport_size({'width':390,'height':844});page.locator('#meetingPreview').scroll_into_view_if_needed()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),theme
                page.screenshot(path=str(ART/f'v5.0.15-{theme}-meeting-mobile.png'))
            assert not errors,errors
            browser.close()
        print('PASS: DOCX reading, no-config/402 input retention, source preview, person mapping, partial save, library/project integration, custom background, deduplication, refresh recovery, four mobile themes. TEST DOUBLE only.')
    finally:
        proc.terminate();proc.wait(timeout=10);mock.shutdown();mock.server_close()
