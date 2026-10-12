"""Real Chromium end-to-end tests against a clearly identified model TEST DOUBLE."""
import json
import os
import pathlib
import subprocess
import socket
import sys
import tempfile
import time
import urllib.request
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from fake_provider import start,Provider
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(__file__).resolve().parents[1]
ART=pathlib.Path(os.environ.get('COACH_TEST_ARTIFACTS','/tmp/workplace-browser-artifacts'));ART.mkdir(exist_ok=True,parents=True)
with tempfile.TemporaryDirectory() as data:
    mock=start();env={**os.environ,'COACH_DATA_ROOT':data,'AHC_NO_OPEN':'1'}
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    process=subprocess.Popen([sys.executable,'server.py',str(port)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        url='http://127.0.0.1:'+str(port)
        for _ in range(80):
            try:
                urllib.request.urlopen(url+'/api/workplace/workspace').close();break
            except Exception:time.sleep(.1)
        else:raise RuntimeError('Server did not start')
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=os.environ.get('COACH_CHROMIUM','/usr/bin/chromium'),headless=True)
            context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
            page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(url);expect(page.locator('#sceneTitle')).to_contain_text('项目进度');page.screenshot(path=str(ART/'desktop-home.png'),full_page=True)
            assert page.locator('#start').is_enabled()
            # No key/config: genuine error, no fake opening.
            page.click('#start');expect(page.locator('#globalError')).to_contain_text('API 设置');assert page.locator('.bubble').count()==0
            page.click('#apiOpen');expect(page.locator('#apiName')).to_have_value('DeepSeek527');expect(page.locator('#apiURL')).to_have_value('https://api.deepseek.com');expect(page.locator('#apiModel')).to_have_value('deepseek-flash');expect(page.locator('#apiKey')).to_have_value('');page.fill('#apiName','浏览器验收 · 测试替身');page.fill('#apiURL',f'http://127.0.0.1:{mock.server_port}/v1');page.fill('#apiModel','dialog-model');page.fill('#apiReviewModel','review-model');page.click('#apiForm button[type=submit]');expect(page.locator('#apiStatus')).to_contain_text('已保存');page.click('#apiTest');expect(page.locator('#apiStatus')).to_contain_text('连接测试通过');page.click('[data-close=apiDialog]')
            # Multi-config add/switch.
            page.click('#apiOpen');page.click('#apiNew');page.fill('#apiName','第二配置');page.fill('#apiURL',f'http://127.0.0.1:{mock.server_port}/custom/chat/completions');page.fill('#apiModel','second-model');page.click('#apiForm button[type=submit]');expect(page.locator('#apiStatus')).to_contain_text('已保存');options=page.locator('#apiSelect option').all();assert len(options)==3
            first=page.locator('#apiSelect option').nth(1).get_attribute('value');page.select_option('#apiSelect',first);page.click('#apiActivate');expect(page.locator('#apiBadge')).to_have_text('浏览器验收 · 测试替身');page.click('[data-close=apiDialog]')
            # Object create/edit and snapshot freeze.
            page.click('[data-tab=objects]');page.click('#newObject');page.fill('[name=name]','协作对象');page.fill('[name=role]','项目协作伙伴');page.fill('[name=goals]','保障交付');page.fill('[name=standards]','事实明确、行动可执行');page.fill('[name=style]','合作且直接');page.click('#objectForm button');expect(page.locator('#objectDialog')).not_to_be_visible();expect(page.locator('#objectCards')).to_contain_text('协作对象')
            page.click('[data-tab=practice]');page.click('#start');expect(page.locator('.bubble')).to_have_count(1);expect(page.locator('#chat')).to_contain_text('请说明方案');page.fill('#reply','我建议先验证，已完成8项测试，我负责明天更新结果。');page.click('#send');expect(page.locator('.bubble')).to_have_count(3);page.fill('#reply','需要您确认优先级，剩余风险由双方共同核查。');page.click('#send');expect(page.locator('.bubble')).to_have_count(5)
            page.locator('.bubble details summary').first.click();expect(page.locator('.interpretation').first).to_be_visible()
            page.reload();expect(page.locator('.bubble')).to_have_count(5);page.screenshot(path=str(ART/'desktop-training.png'),full_page=True)
            # Portrait fails after successful review, retained and retried.
            Provider.mode='portrait-fail';page.click('#end');expect(page.locator('#review')).to_be_visible();expect(page.locator('.bigscore')).to_contain_text('59');expect(page.locator('.round')).to_have_count(2);expect(page.locator('#review')).to_contain_text('长期画像生成失败');page.screenshot(path=str(ART/'desktop-review.png'),full_page=True)
            Provider.mode='ok';page.click('[data-tab=portrait]');page.click('#portraitRetry');expect(page.locator('#portraitContent')).to_contain_text('2 条回应');page.reload();page.click('[data-tab=portrait]');expect(page.locator('#portraitContent')).to_contain_text('2 条回应')
            # Export offline HTML contains SVG, all messages, and no API secrets.
            page.click('[data-tab=practice]')
            with page.expect_download() as dl:page.click('#exportHTML')
            export=ART/'review.html';dl.value.save_as(export);content=export.read_text();assert '<svg' in content and '我建议先验证' in content and '原话三层解读' in content and 'apiKey' not in content
            page.emulate_media(media='print');page.pdf(path=str(ART/'review.pdf'),format='A4',print_background=True);page.emulate_media(media='screen');assert (ART/'review.pdf').stat().st_size>10000
            report=context.new_page();report.route('**/*',lambda route:route.abort());report.set_content(content);expect(report.locator('.radar')).to_be_visible();assert report.locator('details:not([open])').count()==0;assert report.locator('link,script,img[src]').count()==0;report.screenshot(path=str(ART/'standalone-report.png'),full_page=True);report.close()
            # English training with a failed send and a single retry.
            page.click('#again');page.click('[data-category=english]');page.click('[data-scene=en-delay]');page.click('#start');expect(page.locator('#chat')).to_contain_text('What evidence');Provider.mode='http';page.fill('#reply','I will send an update by Friday.');page.click('#send');expect(page.locator('#sessionError')).to_contain_text('HTTP 503');expect(page.locator('.bubble.user')).to_have_count(1);assert page.locator('#send').is_disabled();Provider.mode='ok';page.click('#retry');expect(page.locator('.bubble')).to_have_count(3);expect(page.locator('.bubble.user')).to_have_count(1);page.click('#end');expect(page.locator('#review')).to_be_visible();expect(page.locator('.demo')).to_contain_text('I will confirm')
            # Mobile layout and radar labels.
            page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(ART/'mobile-review.png'),full_page=True)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'mobile page has horizontal overflow'
            assert page.locator('.radar text').count()==11
            page.click('#back');page.screenshot(path=str(ART/'mobile-home.png'),full_page=True);assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            # Archived records remain inspectable, newer rounds do not reuse old messages.
            page.click('[data-tab=history]');expect(page.locator('#records .record')).to_have_count(2);page.locator('#records [data-open-session]').first.click();expect(page.locator('#chat')).to_contain_text('I will send an update')
            page.click('#back');page.click('#start');expect(page.locator('.bubble')).to_have_count(1)
            Provider.mode='http';page.fill('#reply','Keep this reply when changing API.');page.click('#send');expect(page.locator('#sessionError')).to_contain_text('HTTP 503');Provider.mode='ok'
            page.click('#apiOpen');page.click('#apiNew');page.fill('#apiName','修复回归配置');page.fill('#apiURL',f'http://127.0.0.1:{mock.server_port}/v1');page.fill('#apiModel','replacement-model');page.click('#apiForm button[type=submit]');expect(page.locator('#apiStatus')).to_contain_text('已保存');page.select_option('#apiSelect',first);page.once('dialog',lambda d:d.accept());page.click('#apiDelete');expect(page.locator('#apiBadge')).to_have_text('修复回归配置');page.click('#apiTest');expect(page.locator('#apiStatus')).to_contain_text('本轮仍绑定旧配置');page.click('[data-close=apiDialog]');expect(page.locator('#sessionError')).to_contain_text('旧 API 配置已不存在');page.click('#useCurrentAPI');page.click('#retry');expect(page.locator('.bubble')).to_have_count(3);expect(page.locator('.bubble.user')).to_have_count(1);expect(page.locator('#sessionError')).not_to_be_visible()
            page.once('dialog',lambda d:d.accept());page.click('#cancel');expect(page.locator('#sessionMeta')).to_contain_text('已中断');assert page.locator('#exportHTML').is_hidden();assert page.locator('#print').is_hidden();assert page.locator('#exportJSON').is_visible()
            assert not errors, errors
            browser.close()
        print('PASS: desktop/mobile, no-config error, API CRUD/switch/test, object CRUD, two-turn training, refresh recovery, failed-send retry, portrait failure/retry, English review, HTML/PDF export; no page errors. TEST DOUBLE only.')
        print('Artifacts:',ART)
    finally:
        process.terminate();process.wait(timeout=10);mock.shutdown();mock.server_close()
