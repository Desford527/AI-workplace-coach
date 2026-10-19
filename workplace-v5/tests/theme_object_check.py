"""Chromium acceptance: PPT colors, four persistent themes and object deletion.
All model requests go only to the local TEST DOUBLE in fake_provider.py.
"""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fake_provider import Provider, start
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ART = Path(os.environ.get('COACH_TEST_ARTIFACTS', '/tmp/workplace-browser-artifacts'))
ART.mkdir(parents=True, exist_ok=True)
PALETTES = {
    'corporate': ('企业红', 'rgb(199, 0, 25)', 'rgb(255, 248, 246)'),
    'forest': ('纸色深绿', 'rgb(23, 79, 64)', 'rgb(23, 79, 64)'),
    'ocean': ('晴空蓝', 'rgb(22, 76, 114)', 'rgb(22, 76, 114)'),
    'violet': ('雾紫', 'rgb(87, 65, 111)', 'rgb(87, 65, 111)'),
}

with tempfile.TemporaryDirectory() as data:
    mock = start()
    Provider.mode = 'ok'
    Provider.calls = []
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    env = {**os.environ, 'COACH_DATA_ROOT': data, 'AHC_NO_OPEN': '1', 'COACH_DISABLE_BUNDLED_DEFAULTS': '1'}
    process = subprocess.Popen([sys.executable, 'server.py', str(port)], cwd=ROOT, env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = 'http://127.0.0.1:' + str(port)
    try:
        for _ in range(80):
            try:
                urllib.request.urlopen(url + '/api/workplace/workspace').close()
                break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError('Server did not start')
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get('COACH_CHROMIUM', '/usr/bin/chromium'), headless=True)
            context = browser.new_context(viewport={'width':1440, 'height':1000}, accept_downloads=True)
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(url)
            expect(page.locator('#sceneTitle')).to_contain_text('项目进度')
            expect(page.locator('html')).to_have_attribute('data-theme', 'corporate')
            assert '↗' not in page.locator('body').inner_text()
            expect(page.locator('#previewAvatar')).to_have_text('朱')
            expect(page.locator('#previewRole')).to_have_text('朱总：项目负责人')
            expect(page.locator('#objectSelect option[value=builtin-project]')).to_have_text('朱总：项目负责人')
            expect(page.locator('#objectSelect option[value=builtin-technical]')).to_have_text('严工：技术评审专家')
            page.click('[data-tab=objects]')
            expect(page.locator('#objectCards .object-card')).to_have_count(4)
            expect(page.locator('#objectCards')).to_contain_text('严工：技术评审专家')
            assert '啦啦啦' not in page.locator('#objectCards').inner_text()
            assert '张总' not in page.locator('#objectCards').inner_text()
            zhu=page.locator('.object-card').filter(has_text='朱总：项目负责人')
            zhu.locator('details > summary').click()
            expect(zhu).to_contain_text('性格与沟通习惯')
            expect(zhu).to_contain_text('IGBT/SiC')
            zhu.locator('[data-edit-object]').click()
            expect(page.locator('[name=personality]')).to_contain_text('情绪不外露')
            expect(page.locator('[name=technicalBackground]')).to_contain_text('壳温')
            page.click('[data-close=objectDialog]')
            page.click('[data-tab=practice]')
            expect(page.locator('.mark svg')).to_have_count(1)
            page.screenshot(path=str(ART / 'v5.0.15-corporate-home.png'), full_page=True)

            def choose_theme(ident):
                page.click('#themeOpen')
                expect(page.locator('#themeChoices button')).to_have_count(4)
                page.click('[data-theme-choice=' + ident + ']')
                expect(page.locator('[data-theme-choice=' + ident + ']')).to_have_attribute('aria-pressed', 'true')
                expect(page.locator('#themeChoices [aria-pressed=true]')).to_have_count(1)
                page.click('[data-close=themeDialog]')
                expect(page.locator('html')).to_have_attribute('data-theme', ident)
                expect(page.locator('#themeName')).to_have_text(PALETTES[ident][0])

            # Theme changes do not send model requests or alter API settings.
            for ident, (name, brand, stage) in PALETTES.items():
                choose_theme(ident)
                expect(page.locator('#start')).to_have_css('background-color', brand)
                expect(page.locator('.opening-stage')).to_have_css('background-color', stage)
                page.reload()
                expect(page.locator('#sceneTitle')).to_contain_text('项目进度')
                expect(page.locator('html')).to_have_attribute('data-theme', ident)
                page.screenshot(path=str(ART / ('v5.0.15-' + ident + '-home-viewport.png')))
                page.set_viewport_size({'width':390, 'height':844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), ident + ' mobile overflow'
                page.click('#themeOpen')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                expect(page.locator('#themeChoices [aria-pressed=true]')).to_have_count(1)
                page.screenshot(path=str(ART / ('v5.0.15-' + ident + '-picker-mobile.png')))
                page.click('[data-close=themeDialog]')
                page.set_viewport_size({'width':1440, 'height':1000})
            # Another tab follows the stored selection.
            other = context.new_page()
            other.goto(url)
            page.evaluate("localStorage.setItem('workplace_theme','forest')")
            expect(other.locator('html')).to_have_attribute('data-theme', 'forest')
            other.close()
            page.evaluate("localStorage.setItem('workplace_theme','invalid-theme')")
            page.reload()
            expect(page.locator('html')).to_have_attribute('data-theme', 'corporate')
            assert not Provider.calls

            def create_object(name):
                page.fill('[name=name]', name)
                page.fill('[name=role]', '项目协作伙伴')
                page.fill('[name=goals]', '保障交付')
                page.fill('[name=standards]', '事实明确、行动可执行')
                page.fill('[name=style]', '合作且直接')
                page.click('#objectForm button[type=submit]')
                expect(page.locator('#objectDialog')).not_to_be_visible()

            page.click('[data-tab=objects]')
            page.click('#newObject')
            create_object('待删除对象')
            card = page.locator('.object-card').filter(has_text='待删除对象')
            expect(card).to_have_count(1)
            page.once('dialog', lambda d:d.dismiss())
            card.locator('[data-delete-object]').click()
            expect(card).to_have_count(1)
            page.once('dialog', lambda d:d.accept())
            card.locator('[data-delete-object]').click()
            expect(card).to_have_count(0)
            assert '待删除对象' not in page.locator('#objectSelect').inner_text()
            page.reload()
            page.click('[data-tab=objects]')
            expect(card).to_have_count(0)

            # Delete the selected built-in during a session, then continue/review it.
            response = page.request.post(url + '/api/workplace/action', data={
                'operation':'config', 'requestId':'test-config',
                'api':{'name':'主题验收 · 测试替身', 'baseURL':f'http://127.0.0.1:{mock.server_port}/v1',
                       'model':'test-model', 'useLLM':True}})
            assert response.ok
            page.reload()
            # Record quotes, inspect evidence-based inference, refresh and invalidate it.
            page.click('[data-tab=objects]')
            page.click('[data-object-quotes=builtin-project]')
            expect(page.locator('#quotesDialog')).to_be_visible()
            raw_quotes='先把测试条件说清楚。\n需要我做什么决定？'
            page.fill('#objectQuotes',raw_quotes)
            page.click('#quotesAnalyze')
            expect(page.locator('#quotesStatus')).to_contain_text('语录与 AI 分析已保存')
            expect(page.locator('#quoteAnalysis')).to_contain_text('倾向明确证据')
            expect(page.locator('#quoteAnalysis')).to_contain_text('可能的表达 · AI 模拟')
            assert page.locator('#objectQuotes').input_value()==raw_quotes
            page.locator('#quoteAnalysis details > summary').first.click()
            expect(page.locator('#quoteAnalysis .quote-evidence').first).to_have_text(raw_quotes.splitlines()[0])
            page.screenshot(path=str(ART/'v5.0.15-quote-analysis.png'))
            page.click('[data-close=quotesDialog]')
            page.reload();page.click('[data-tab=objects]');page.click('[data-object-quotes=builtin-project]')
            expect(page.locator('#objectQuotes')).to_have_value(raw_quotes)
            expect(page.locator('#quoteAnalysis')).to_contain_text('倾向明确证据')
            page.fill('#objectQuotes',raw_quotes+'\n请明确下一次更新时间。')
            page.click('#quotesSave');expect(page.locator('#quotesStatus')).to_have_text('语录已保存，供新训练参考。')
            expect(page.locator('#quoteAnalysis')).to_contain_text('原分析已失效')
            page.click('#quotesAnalyze');expect(page.locator('#quotesStatus')).to_contain_text('语录与 AI 分析已保存')
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=str(ART/'v5.0.15-quote-analysis-mobile.png'))
            page.set_viewport_size({'width':1440,'height':1000})
            page.click('[data-close=quotesDialog]');page.click('[data-tab=practice]')
            page.click('#start')
            expect(page.locator('.bubble')).to_have_count(1)
            page.fill('#reply', '我建议先核实当前结果，并请您确认资源优先级。')
            page.click('#send')
            expect(page.locator('.bubble')).to_have_count(3)
            session_id = page.evaluate("localStorage.getItem('workplace_active_session')")
            original = page.request.get(url + '/api/workplace/session?id=' + session_id).json()
            assert original['object']['quoteAnalysis']['sampleCount']==3
            assert original['object']['quotes'].startswith(raw_quotes)
            page.click('[data-tab=objects]')
            page.once('dialog', lambda d:d.accept())
            page.click('[data-delete-object=builtin-project]')
            expect(page.locator('[data-delete-object=builtin-project]')).to_have_count(0)
            assert page.request.get(url + '/api/workplace/session?id=' + session_id).json() == original
            page.click('[data-tab=practice]')
            page.fill('#reply', '我负责明天更新核查结果，未知项会明确标注。')
            page.click('#send')
            expect(page.locator('.bubble')).to_have_count(5)
            Provider.mode='details-fail'
            page.click('#end')
            expect(page.locator('.bigscore')).to_be_visible()
            expect(page.locator('#back')).to_be_enabled()
            expect(page.locator('[data-review-details]')).to_be_enabled()
            expect(page.locator('#sessionError')).not_to_be_visible()
            expect(page.locator('#review')).to_contain_text('六维评分与原话依据已保存')
            page.screenshot(path=str(ART/'v5.0.15-partial-review.png'),full_page=True)
            before=page.request.get(url+'/api/workplace/session?id='+session_id).json()
            Provider.mode='ok';page.click('[data-review-details]')
            expect(page.locator('[data-review-details]')).to_have_count(0)
            expect(page.locator('.demo').first).to_contain_text('模型替身补全示范')
            after=page.request.get(url+'/api/workplace/session?id='+session_id).json()
            assert before['review']['dims']==after['review']['dims'] and before['messages']==after['messages']
            count = len(Provider.calls)
            for ident, (_, brand, stage) in PALETTES.items():
                choose_theme(ident)
                assert page.locator('.review-verdict').evaluate('(e)=>getComputedStyle(e).backgroundColor') == stage
                assert page.locator('.radar .shape').evaluate('(e)=>getComputedStyle(e).stroke') == brand
                page.evaluate('window.scrollTo(0,0)')
                page.screenshot(path=str(ART / ('v5.0.15-' + ident + '-review.png')), full_page=True)
                page.set_viewport_size({'width':390, 'height':844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.set_viewport_size({'width':1440, 'height':1000})
            assert len(Provider.calls) == count
            choose_theme('ocean')
            with page.expect_download() as dl:
                page.click('#exportHTML')
            export = ART / 'v5.0.15-ocean-report.html'
            dl.value.save_as(export)
            content = export.read_text()
            assert 'data-theme="ocean"' in content
            report = context.new_page()
            report.route('**/*', lambda route:route.abort())
            report.set_content(content)
            assert report.locator('.review-verdict').evaluate('(e)=>getComputedStyle(e).backgroundColor') == PALETTES['ocean'][2]
            assert report.locator('details:not([open])').count() == 0
            assert report.locator('script,link,img[src]').count() == 0
            report.close()
            choose_theme('corporate')

            # Fallback selection, deleting the last object, and creating again.
            page.click('#again')
            assert page.locator('#objectSelect').input_value() not in ('', 'builtin-project')
            page.click('[data-tab=objects]')
            page.screenshot(path=str(ART / 'v5.0.15-object-delete.png'), full_page=True)
            while page.locator('[data-delete-object]').count():
                previous = page.locator('[data-delete-object]').count()
                page.once('dialog', lambda d:d.accept())
                page.locator('[data-delete-object]').first.click()
                expect(page.locator('[data-delete-object]')).to_have_count(previous - 1)
            page.reload()
            expect(page.locator('#noObjects')).to_be_visible()
            expect(page.locator('#start')).to_be_disabled()
            expect(page.locator('#objectSelect')).to_be_disabled()
            expect(page.locator('#objectFocus')).not_to_be_visible()
            page.click('[data-category=technical]')
            expect(page.locator('#start')).to_be_disabled()
            page.screenshot(path=str(ART / 'v5.0.15-empty-objects.png'), full_page=True)
            page.click('[data-create-object]')
            create_object('重新创建的对象')
            expect(page.locator('#noObjects')).not_to_be_visible()
            expect(page.locator('#start')).to_be_enabled()
            expect(page.locator('#objectSelect')).to_contain_text('重新创建的对象')
            page.click('[data-tab=history]')
            expect(page.locator('#records .record')).to_have_count(1)
            page.click('#records [data-open-session]')
            expect(page.locator('.bigscore')).to_be_visible()
            expect(page.locator('#review')).to_contain_text('项目负责人')
            assert not errors, errors
            browser.close()
        print('PASS: four PPT-based/preserved themes, persistence and cross-tab sync, mobile, themed offline export; custom/builtin deletion, confirmation/cancel, frozen history, continuation/review and empty-state recovery. TEST DOUBLE only.')
        print('Artifacts:', ART)
    finally:
        process.terminate()
        process.wait(timeout=10)
        mock.shutdown()
        mock.server_close()
