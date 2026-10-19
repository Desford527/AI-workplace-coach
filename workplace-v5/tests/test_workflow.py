import copy
import json
import os
import pathlib
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request
import uuid
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
sys.argv=[sys.argv[0]]
os.environ['COACH_DISABLE_BUNDLED_DEFAULTS']='1'
import server
import workplace as w
from fake_provider import Provider,start

class Workflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provider=start()
        cls.http=server.http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        threading.Thread(target=cls.http.serve_forever,daemon=True).start()
        cls.url='http://127.0.0.1:'+str(cls.http.server_port)
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown();cls.http.server_close();cls.provider.shutdown();cls.provider.server_close()
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();root=pathlib.Path(self.tmp.name)
        server.DATA_ROOT=str(root);server.CONFIG_PATH=str(root/'user_data'/'apiconfig.json')
        w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server)
        Provider.mode='ok';Provider.calls=[]
        w.atomic_config({'apis':[{'id':'p1','name':'替身','baseURL':f'http://127.0.0.1:{self.provider.server_port}/v1','apiKey':'not-a-real-key','model':'dialog-model','reviewModel':'review-model','useLLM':True}],'active':'p1'})
    def tearDown(self): self.tmp.cleanup()
    def call(self,op,**data):
        raw=json.dumps({'operation':op,'requestId':str(uuid.uuid4()),**data}).encode()
        req=urllib.request.Request(self.url+'/api/workplace/action',data=raw,headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req) as r:return json.load(r)
    def begin(self,scene='progress'):
        return self.call('start',sceneId=scene,objectId='builtin-project',goal='明确推进决策',background='脱敏背景',intensity='标准')
    def send(self,s,t='我的判断是按计划推进，已完成8项测试；我负责明天更新结果。'):
        return self.call('send',sessionId=s['id'],revision=s['revision'],text=t)
    def review(self,s):return self.call('review',sessionId=s['id'],revision=s['revision'])
    def test_complete_two_turns_and_persistence(self):
        self.assertIsNone(w.get('portrait','self'))
        s=self.begin();self.assertEqual(s['messages'][0]['role'],'assistant')
        s=self.send(s);s=self.send(s,'请确认优先级，我会同步风险。');s=self.review(s)
        self.assertEqual(s['status'],'reviewed');r=s['review'];self.assertEqual(len(r['dims']),6);self.assertEqual(len(r['timeline']),2)
        self.assertEqual(r['score'],59);self.assertTrue(all(t['score']==59 for t in r['timeline']))
        self.assertEqual(s['portraitStatus'],'updated');self.assertEqual(w.get('portrait','self')['sampleCount'],2)
        self.assertEqual(w.get('session',s['id'])['review'],r)
        self.assertEqual(Provider.calls[-2]['body']['model'],'review-model')
        self.assertEqual(Provider.calls[1]['body']['model'],'dialog-model')
        self.assertIn(s['messages'][0]['text'],str(Provider.calls[2]['body']))
    def test_failed_send_preserves_and_retries(self):
        s=self.begin();Provider.mode='http'
        with self.assertRaises(urllib.error.HTTPError):self.send(s,'保留这句用户原话')
        s=w.get('session',s['id']);self.assertEqual(s['messages'][-1]['text'],'保留这句用户原话')
        with self.assertRaises(urllib.error.HTTPError):self.send(s,'重复不应进入')
        Provider.mode='ok';s=self.call('retry',sessionId=s['id'],revision=s['revision'])
        self.assertEqual(len([m for m in s['messages'] if m['role']=='user']),1)
        self.assertEqual(s['messages'][-1]['role'],'assistant')
    def test_review_protocol_failures(self):
        for mode in ('json','bad-score','missing-dim','bad-evidence','missing-turn','bad-quote','bad-round'):
            with self.subTest(mode=mode):
                Provider.mode='ok';s=self.send(self.begin());Provider.mode=mode
                with self.assertRaises(urllib.error.HTTPError):self.review(s)
                self.assertNotIn('review',w.get('session',s['id']))
    def test_portrait_failure_does_not_lose_review(self):
        s=self.send(self.begin());Provider.mode='portrait-fail';s=self.review(s)
        self.assertEqual(s['status'],'reviewed');self.assertEqual(s['portraitStatus'],'failed');self.assertIsNone(w.get('portrait','self'))
        Provider.mode='ok';p=self.call('portrait');self.assertEqual(p['sessionCount'],1)
    def test_snapshot_survives_object_edit(self):
        s=self.begin();o=copy.deepcopy(s['object']);o['goals']='修改后的目标';self.call('object',object=o)
        self.assertNotEqual(w.get('session',s['id'])['object']['goals'],'修改后的目标')
    def test_delete_builtin_preserves_session_and_portrait(self):
        s=self.send(self.begin());s=self.review(s)
        snapshot=copy.deepcopy(s);portrait=copy.deepcopy(w.get('portrait','self'));config=copy.deepcopy(w.config_store())
        result=self.call('delete-object',objectId='builtin-project')
        self.assertTrue(result['deleted']);self.assertNotIn('builtin-project',[o['id'] for o in w.objects()])
        self.assertEqual(w.get('session',s['id']),snapshot)
        self.assertEqual(w.get('portrait','self'),portrait);self.assertEqual(w.config_store(),config)
        with self.assertRaises(urllib.error.HTTPError) as cm:self.begin()
        self.assertEqual(cm.exception.code,400)
        w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server)
        self.assertNotIn('builtin-project',[o['id'] for o in w.objects()])
    def test_deleted_legacy_and_edited_builtin_do_not_reappear(self):
        coach={'id':'c_fixture','name':'额外测试对象','role':'协作对象'}
        with patch.object(server,'load_manifest',return_value={'coaches':[coach]}), patch.object(server,'assemble_coach',return_value={'quotes':[]}):
            w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server)
            imported=next(o for o in w.objects() if o['id']=='legacy-c_fixture')
            builtin=next(o for o in w.objects() if o['id']=='builtin-technical')
            builtin['goals']='编辑后的目标';self.call('object',object=builtin)
            for o in (imported,builtin):self.call('delete-object',objectId=o['id'])
            w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server)
            ids={o['id'] for o in w.objects()};self.assertNotIn(imported['id'],ids);self.assertNotIn(builtin['id'],ids)
            with self.assertRaises(urllib.error.HTTPError) as cm:self.call('object',object=builtin)
            self.assertEqual(cm.exception.code,409)
    def test_delete_custom_idempotent_and_active_session_continues(self):
        o=copy.deepcopy(w.objects()[0]);o.pop('id');o=self.call('object',object=o)
        s=self.call('start',sceneId='progress',objectId=o['id'])
        rid=str(uuid.uuid4());out=self.call('delete-object',requestId=rid,objectId=o['id'])
        self.assertEqual(self.call('delete-object',requestId=rid,objectId=o['id']),out)
        self.assertIsNone(w.get('object',o['id']))
        s=self.review(self.send(s));self.assertEqual(s['status'],'reviewed');self.assertEqual(s['object'],o)
        with self.assertRaises(urllib.error.HTTPError) as cm:self.call('delete-object',objectId='missing')
        self.assertEqual(cm.exception.code,404)
    def test_delete_all_objects_then_create(self):
        for o in w.objects():self.call('delete-object',objectId=o['id'])
        self.assertEqual(w.objects(),[])
        w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server);self.assertEqual(w.objects(),[])
        o=copy.deepcopy(w.CATALOG['objects'][0]);o.pop('id');o=self.call('object',object=o)
        self.assertEqual(len(w.objects()),1)
        self.assertEqual(self.call('start',sceneId='progress',objectId=o['id'])['object'],o)
    def reset_roster_migration(self):
        with w.db() as c:c.execute('DELETE FROM meta WHERE id=?',('object-roster:'+w.ROSTER_VERSION,))
    def test_curated_roster_fresh_and_original_interfaces(self):
        roster=w.objects();self.assertEqual(len(roster),4)
        self.assertEqual([o['name'] for o in roster[:2]],['朱总：项目负责人','严工：技术评审专家'])
        self.assertFalse(any(o['id'].startswith('legacy-') for o in roster))
        with urllib.request.urlopen(self.url+'/api/coach/zhangzong') as r:coach=json.load(r)
        self.assertIn('朱总',str(coach));self.assertIn('变流',str(coach))
        self.assertFalse(any(c['name']=='啦啦啦' for c in server.load_manifest()['coaches']))
    def test_roster_merge_archives_sources_preserves_history_config(self):
        s=self.review(self.send(self.begin()));snapshot=copy.deepcopy(s)
        portrait=copy.deepcopy(w.get('portrait','self'));cfg=copy.deepcopy(w.config_store())
        p=copy.deepcopy(w.CATALOG['objects'][0]);p.update(id='legacy-zhangzong',name='张总',style='原来记录的表达习惯')
        y=copy.deepcopy(w.CATALOG['objects'][1]);y.update(id='legacy-yanlaoshi',name='严工')
        dummy={**p,'id':'legacy-c_cnbg1swm','name':'啦啦啦'}
        extra={**p,'id':'custom-keep','name':'独立客户'}
        for o in (p,y,dummy,extra):w.save('object',o['id'],o)
        # This fixture represents a pre-merge install with live legacy profiles.
        with w.db() as c:
            for o in (p,y,dummy):c.execute('DELETE FROM docs WHERE kind="deleted-object" AND id=?',(o['id'],))
        self.reset_roster_migration();w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server)
        roster=w.objects();ids={o['id'] for o in roster}
        self.assertEqual(len(roster),5);self.assertTrue({'builtin-project','builtin-technical','custom-keep'}<=ids)
        self.assertFalse({'legacy-zhangzong','legacy-yanlaoshi','legacy-c_cnbg1swm'}&ids)
        archived=w.get('object-archive',w.ROSTER_VERSION+':legacy-zhangzong')
        self.assertEqual(archived['object'],p);self.assertEqual(archived['mergedInto'],'builtin-project')
        self.assertEqual(w.get('session',s['id']),snapshot);self.assertEqual(w.get('portrait','self'),portrait)
        self.assertEqual(w.config_store(),cfg)
        updated=copy.deepcopy(next(o for o in roster if o['id']=='builtin-project'));updated['style']='后续用户修改保留'
        self.call('object',object=updated);w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server)
        self.assertEqual(w.get('object','builtin-project')['style'],'后续用户修改保留')
    def test_live_duplicate_promotes_canonical_but_fully_deleted_stays_deleted(self):
        p=copy.deepcopy(w.CATALOG['objects'][0]);p.update(id='legacy-zhangzong',name='张总')
        self.call('delete-object',objectId='builtin-project');w.save('object',p['id'],p)
        with w.db() as c:c.execute('DELETE FROM docs WHERE kind="deleted-object" AND id=?',(p['id'],))
        self.reset_roster_migration();w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server)
        self.assertIn('builtin-project',[o['id'] for o in w.objects()])
        self.call('delete-object',objectId='builtin-project');self.reset_roster_migration()
        w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server)
        self.assertNotIn('builtin-project',[o['id'] for o in w.objects()])
    def test_name_duplicate_removal_and_legacy_reimport_guard(self):
        for ident,name in [('custom-project','项目负责人'),('custom-review','严工'),('custom-remove','啦啦啦')]:
            w.save('object',ident,{**w.CATALOG['objects'][0],'id':ident,'name':name})
        self.reset_roster_migration()
        coaches=[{'id':'zhangzong','name':'张总'},{'id':'yanlaoshi','name':'严工'},{'id':'c_cnbg1swm','name':'啦啦啦'}]
        with patch.object(server,'load_manifest',return_value={'coaches':coaches}):
            w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server)
            w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server)
        self.assertEqual(len(w.objects()),4)
        self.assertIsNotNone(w.get('deleted-object','custom-remove'))
    def test_profile_extensions_roundtrip_and_reach_model(self):
        p=copy.deepcopy(w.CATALOG['objects'][0]);p['technicalBackground']+='额外技术背景标记'
        out=self.call('object',object=p);self.assertEqual(out['personality'],p['personality'])
        s=self.begin();prompt=Provider.calls[-1]['body']['messages'][0]['content']
        self.assertIn('额外技术背景标记',prompt);self.assertIn('长线权衡',prompt)
        self.assertIn('现代职场专业人员',prompt);self.assertIn('不复刻历史人物身份',prompt)
        self.assertEqual(s['object']['technicalBackground'],p['technicalBackground'])
    def test_config_multi_provider_key_retention(self):
        a={'id':'p1','name':'改名','baseURL':f'http://127.0.0.1:{self.provider.server_port}/v1/chat/completions','model':'new-model','reviewModel':'other-model'}
        out=self.call('config',api=a);self.assertTrue(out['apis'][0]['hasKey']);self.assertNotIn('apiKey',out['apis'][0])
        self.assertEqual(w.config_store()['apis'][0]['apiKey'],'not-a-real-key')
        a['id']='p2';self.call('config',api=a);self.call('config',configOperation='activate',id='p1');self.assertEqual(w.config_store()['active'],'p1')
        self.call('test',apiId='p1');self.assertEqual(Provider.calls[-1]['path'],'/v1/chat/completions')
        self.call('config',configOperation='delete',id='p2');self.assertEqual(len(w.config_store()['apis']),1)
    def test_original_config_interfaces(self):
        with urllib.request.urlopen(self.url+'/api/config') as r: cfg=json.load(r)
        req=urllib.request.Request(self.url+'/api/config',data=json.dumps(cfg).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req) as r:self.assertTrue(json.load(r)['ok'])
        with urllib.request.urlopen(self.url+'/api/manifest') as r:self.assertIn('coaches',json.load(r))
        with urllib.request.urlopen(self.url+'/api/coach/zhangzong') as r:self.assertIn('simulateSystem',json.load(r))
    def test_endpoint_normalization(self):
        for base,expected in [('https://example.com','https://example.com/chat/completions'),('https://example.com/v1/','https://example.com/v1/chat/completions'),('https://example.com/custom/chat/completions?x=1','https://example.com/custom/chat/completions?x=1')]:
            self.assertEqual(w.endpoint_url(base),expected)
        with self.assertRaises(w.Problem):w.endpoint_url('http://example.com')
    def test_idempotent_start_and_stale_revision(self):
        rid=str(uuid.uuid4());args={'requestId':rid,'sceneId':'progress','objectId':'builtin-project'}
        s=self.call('start',**args);again=self.call('start',**args);self.assertEqual(s,again);self.assertEqual(len(Provider.calls),1)
        updated=self.send(s)
        with self.assertRaises(urllib.error.HTTPError) as cm:self.send(s)
        self.assertEqual(cm.exception.code,409)
        self.assertEqual(len(w.get('session',s['id'])['messages']),3)
    def test_cancel_new_session_isolated(self):
        s=self.send(self.begin());s=self.call('cancel',sessionId=s['id'],revision=s['revision'])
        self.assertEqual(s['status'],'archived');new=self.begin();self.assertEqual(len(new['messages']),1)
        with self.assertRaises(urllib.error.HTTPError):self.send(s)
    def test_english_and_scenes(self):
        self.assertEqual(len(w.workspace()['scenes']),8)
        s=self.begin('en-delay');self.assertTrue(s['messages'][0]['text'].startswith('What'))
        s=self.send(s,'I will confirm the requirement by Friday.');s=self.review(s)
        self.assertTrue(s['review']['timeline'][0]['improved'].startswith('I will'))
    def test_legacy_record_untouched_and_reanalysis(self):
        raw={'messages':[{'role':'assistant','text':'请给结论'},{'role':'user','text':'我建议明天验证'}], 'review':{'dims':[{'name':'旧'+str(i),'score':50} for i in range(5)]}}
        old=self.call('import-legacy',record=raw,label='旧五维');self.assertEqual(w.get('legacy',old['id'])['raw'],raw)
        s=self.call('reanalyze-legacy',legacyId=old['id'],sceneId='progress',objectId='builtin-project')
        self.assertEqual(len(s['review']['dims']),6);self.assertEqual(w.get('legacy',old['id'])['raw'],raw)
    def test_cross_site_and_static_privacy(self):
        for path in ('/user_data/apiconfig.json','/skills/manifest.json','/server.py'):
            with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(self.url+path)
        req=urllib.request.Request(self.url+'/api/config',headers={'Origin':'https://evil.example'})
        with self.assertRaises(urllib.error.HTTPError) as cm:urllib.request.urlopen(req)
        self.assertEqual(cm.exception.code,403)
    def test_timeout(self):
        s=self.begin();Provider.mode='delay';os.environ['COACH_MODEL_TIMEOUT']='0.1'
        try:
            with self.assertRaises(urllib.error.HTTPError) as cm:self.send(s,'超时也要保留')
            self.assertEqual(cm.exception.code,504);self.assertEqual(w.get('session',s['id'])['messages'][-1]['text'],'超时也要保留')
        finally:os.environ.pop('COACH_MODEL_TIMEOUT',None)
    def test_portrait_bad_evidence_and_accumulation(self):
        s=self.review(self.send(self.begin()));p=w.get('portrait','self')
        broken=copy.deepcopy(p);broken['traits'][0]['evidence'][0]['quote']='不存在的原话'
        with self.assertRaises(w.Problem):w.validate_portrait(broken,[s])
        self.review(self.send(self.begin()));p=w.get('portrait','self');self.assertEqual(p['sessionCount'],2);self.assertEqual(len(p['history']),1)
    def test_migration_preserves_source_and_refuses_existing_destination(self):
        import migrate_local
        source=pathlib.Path(self.tmp.name)/'old';source.mkdir();(source/'server.py').write_text('old original source')
        (source/'user_data').mkdir();cfg={'apis':[{'id':'old','apiKey':'not-a-real-key','model':'keep-model'}],'active':'old'}
        (source/'user_data'/'apiconfig.json').write_text(json.dumps(cfg));(source/'user_data'/'history.json').write_text('{"old": true}')
        dest=pathlib.Path(self.tmp.name)/'new'
        migrate_local.migrate(source,dest)
        self.assertEqual(json.loads((dest/'user_data'/'apiconfig.json').read_text()),cfg)
        self.assertEqual((source/'server.py').read_text(),'old original source')
        self.assertTrue((dest/'legacy-backup'/'user_data'/'history.json').exists())
        with self.assertRaises(ValueError):migrate_local.migrate(source,dest)
        with self.assertRaises(ValueError):migrate_local.migrate(source,source/'new')
    def test_original_coach_crud_quotes(self):
        def legacy(path,payload=None,method=None):
            req=urllib.request.Request(self.url+path,data=json.dumps(payload).encode() if payload is not None else None,
                   headers={'Content-Type':'application/json'},method=method)
            with urllib.request.urlopen(req) as r:return json.load(r)
        created=legacy('/api/coach',{'name':'API兼容对象','role':'技术专家','persona':'虚拟专家','scenes':[{'label':'技术汇报','opening':'请给结论'}]})
        ident=created['coach']['id'];detail=legacy('/api/coach/'+ident);self.assertIn('虚拟专家',detail['persona'])
        legacy('/api/coach/update',{'id':ident,'name':'API修改对象','role':'工程专家','persona':'已修改'})
        self.assertEqual(legacy('/api/coach/'+ident)['name'],'API修改对象')
        legacy('/api/quotes/'+ident,{'quotes':['请说明依据']});self.assertIn('请说明依据',legacy('/api/quotes/'+ident)['quotes'])
        self.assertTrue(legacy('/api/coach/'+ident,method='DELETE')['ok'])
    def test_invalid_json_start_has_recoverable_session(self):
        Provider.mode='json';rid=str(uuid.uuid4())
        with self.assertRaises(urllib.error.HTTPError):self.call('start',requestId=rid,sceneId='progress',objectId='builtin-project')
        s=w.get('session',rid);self.assertIsNotNone(s);self.assertEqual(len(s['messages']),0)
        Provider.mode='ok';s=self.call('retry',sessionId=rid,revision=s['revision']);self.assertEqual(len(s['messages']),1)
    def test_test_connection_does_not_rebind_old_training(self):
        s=self.begin();Provider.mode='http'
        with self.assertRaises(urllib.error.HTTPError):self.send(s,'配置切换也要保留原话')
        s=w.get('session',s['id']);before=copy.deepcopy(s)
        self.call('config',api={'id':'new-api','name':'新配置','baseURL':f'http://127.0.0.1:{self.provider.server_port}/v1','model':'new-model'})
        self.call('config',configOperation='delete',id='p1');Provider.mode='ok'
        self.assertTrue(self.call('test',apiId='new-api')['ok'])
        with self.assertRaises(urllib.error.HTTPError) as cm:self.call('retry',sessionId=s['id'],revision=s['revision'])
        self.assertIn('本轮绑定',json.load(cm.exception)['error'])
        s=w.get('session',s['id']);s=self.call('use-current-api',sessionId=s['id'],revision=s['revision'])
        self.assertEqual(s['apiId'],'new-api');self.assertEqual(s['messages'],before['messages']);self.assertEqual(s['object'],before['object'])
        s=self.call('retry',sessionId=s['id'],revision=s['revision'])
        self.assertEqual(len([m for m in s['messages'] if m['role']=='user']),1)
        self.assertEqual(Provider.calls[-1]['body']['model'],'new-model')
        self.assertEqual(s['apiChanges'][0]['from'],'p1')
    def test_payment_error_explains_balance_and_preserves_reply(self):
        s=self.begin();Provider.mode='payment'
        with self.assertRaises(urllib.error.HTTPError) as cm:self.send(s,'余额不足时保留原话')
        error=json.load(cm.exception)['error'];self.assertIn('HTTP 402',error);self.assertIn('余额不足',error)
        self.assertEqual(w.get('session',s['id'])['messages'][-1]['text'],'余额不足时保留原话')
    def test_replace_legacy_default_updates_name_models_and_key(self):
        s=self.begin();store=w.config_store();store['apis'][0].update(name='deepseek-cbx',model='deepseek-v4-flash',reviewModel='deepseek-v4-flash');w.atomic_config(store)
        self.call('config',api={'id':'other','name':'其他配置','baseURL':'https://example.com','model':'other'})
        self.call('config',configOperation='activate',id='p1')
        with self.assertRaises(urllib.error.HTTPError):self.call('config',configOperation='replace-deepseek-default',apiKey='')
        self.assertEqual(w.selected_config()['name'],'deepseek-cbx')
        replacement='sk-'+('a'*32)
        public=self.call('config',configOperation='replace-deepseek-default',apiKey=replacement)
        self.assertEqual(len(public['apis']),1);a=public['apis'][0];self.assertEqual(a['name'],'DeepSeek527');self.assertEqual(a['model'],'deepseek-flash');self.assertEqual(a['reviewModel'],'');self.assertNotIn('apiKey',a)
        self.assertEqual(w.selected_config()['apiKey'],replacement)
        self.assertEqual(w.selected_config(s['apiId'])['id'],'p1')
        self.assertEqual(w.get('session',s['id'])['messages'],s['messages'])
    def test_bundled_default_replaces_existing_legacy_on_startup(self):
        s=self.begin();store=w.config_store();store['apis'][0].update(name='deepseek-cbx',model='deepseek-v4-flash',reviewModel='deepseek-v4-flash');w.atomic_config(store)
        seed=json.loads((pathlib.Path(server.ROOT)/'default-api.json').read_text())
        w.apply_bundled_defaults();cfg=w.config_store();self.assertEqual(len(cfg['apis']),1);self.assertEqual(cfg['active'],'p1')
        actual={k:v for k,v in cfg['apis'][0].items() if k!='id'};self.assertTrue(actual==seed['api'],'Bundled profile mismatch')
        self.assertEqual(w.get('session',s['id'])['messages'],s['messages'])
        self.assertEqual(cfg['apis'][0]['name'],'DeepSeek527');self.assertEqual(cfg['apis'][0]['model'],'deepseek-flash')
        # Later user edits are preserved after this release has been applied once.
        cfg['apis'][0]['name']='用户后续编辑';w.atomic_config(cfg);w.apply_bundled_defaults();self.assertEqual(w.selected_config()['name'],'用户后续编辑')
    def test_startup_does_not_reuse_older_release(self):
        class OldRelease(server.http.server.BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                data=b'{"version":5,"release":"5.0.4"}'
                self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        old=server.http.server.ThreadingHTTPServer(('127.0.0.1',0),OldRelease)
        threading.Thread(target=old.serve_forever,daemon=True).start()
        try:
            self.assertFalse(server._probe_existing(old.server_port))
            self.assertTrue(server._probe_existing(self.http.server_port))
        finally:old.shutdown();old.server_close()
    def test_model_json_wrappers_and_content_blocks(self):
        for mode in ('fenced','prose','thinking','double-json','blocks'):
            with self.subTest(mode=mode):
                Provider.mode=mode;s=self.begin();self.assertEqual(len(s['messages']),1)
                s=self.send(s);s=self.review(s);self.assertEqual(s['review']['score'],59)
    def test_automatic_format_repair_does_not_duplicate_messages(self):
        Provider.mode='flaky-json';s=self.begin();self.assertEqual(len(Provider.calls),2);self.assertEqual(len(s['messages']),1)
        self.assertIn('上次输出未通过',Provider.calls[-1]['body']['messages'][-1]['content'])
        Provider.mode='ok';s=self.send(s);Provider.mode='flaky-schema';s=self.review(s)
        self.assertEqual(len(s['review']['dims']),6);self.assertEqual(len([m for m in s['messages'] if m['role']=='user']),1)
    def test_invalid_multiple_empty_and_truncated_outputs_stay_failures(self):
        for mode in ('multiple-json','empty','reasoning-only','truncated'):
            with self.subTest(mode=mode):
                Provider.mode=mode;Provider.calls=[]
                with self.assertRaises(urllib.error.HTTPError):self.begin()
                self.assertEqual(len(Provider.calls),2)
                self.assertTrue((pathlib.Path(self.tmp.name)/'user_data/model-response-last-error.json').exists())
    def test_json_mode_unsupported_fallback_is_bounded(self):
        cfg=w.config_store();cfg['apis'][0]['jsonMode']=True;w.atomic_config(cfg);Provider.mode='unsupported-json'
        s=self.begin();self.assertEqual(len(s['messages']),1);self.assertEqual(len(Provider.calls),2)
        self.assertEqual(Provider.calls[0]['body']['response_format'],{'type':'json_object'});self.assertNotIn('response_format',Provider.calls[1]['body'])
    def test_diagnostics_redact_credentials(self):
        c=w.selected_config();w.record_model_error(c,'returned '+c['apiKey'],None,'invalid')
        data=(pathlib.Path(self.tmp.name)/'user_data/model-response-last-error.json').read_text();self.assertNotIn(c['apiKey'],data)
    def test_official_deepseek_request_enables_json_mode(self):
        from unittest.mock import patch
        captured=[]
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,*args):return b'{"choices":[{"message":{"content":"{\\\"ok\\\":true}"},"finish_reason":"stop"}]}'
        class Opener:
            def open(self,request,**kwargs):
                captured.append(json.loads(request.data));return Response()
        c=w.selected_config();c['baseURL']='https://api.deepseek.com'
        with patch.object(w.urllib.request,'build_opener',return_value=Opener()):
            self.assertEqual(w.ask([{'role':'user','content':'Return JSON'}],config=c),{'ok':True})
        self.assertEqual(captured[0]['response_format'],{'type':'json_object'})
    def test_control_characters_and_ambiguous_json(self):
        self.assertEqual(w.parse_model_json('{"line":"first\nsecond"}')['line'],'first\nsecond')
        with self.assertRaises(w.Problem):w.parse_model_json('{"a":1} {"b":2}')
    def test_review_failure_ends_training_and_retry_preserves_messages(self):
        s=self.send(self.begin());before=copy.deepcopy(s['messages']);Provider.mode='missing-dim'
        with self.assertRaises(urllib.error.HTTPError):self.review(s)
        ended=w.get('session',s['id']);self.assertEqual(ended['status'],'review_failed');self.assertEqual(ended['reviewStatus'],'failed');self.assertEqual(ended['messages'],before)
        with self.assertRaises(urllib.error.HTTPError):self.send(ended,'结束后不能继续发送')
        Provider.mode='ok';done=self.review(ended);self.assertEqual(done['status'],'reviewed');self.assertEqual(done['messages'],before)
    def test_review_without_responses_finishes_without_fake_score(self):
        s=self.begin();calls=len(Provider.calls);ended=self.review(s)
        self.assertEqual(ended['status'],'ended');self.assertEqual(ended['reviewStatus'],'empty');self.assertNotIn('review',ended);self.assertEqual(len(Provider.calls),calls)
    def test_review_pending_is_saved_before_model_finishes(self):
        from unittest.mock import patch
        s=self.send(self.begin());original=w.model_review
        def inspect_pending(snapshot):
            current=w.get('session',s['id']);self.assertEqual(current['status'],'review_pending');self.assertTrue(current['endedAt']);return original(snapshot)
        with patch.object(w,'model_review',side_effect=inspect_pending):done=self.review(s)
        self.assertEqual(done['reviewStatus'],'completed')
    def test_restart_recovers_interrupted_review(self):
        s=self.send(self.begin());s['status']='review_pending';s['reviewStatus']='pending';w.save('session',s['id'],s)
        w.recover_interrupted_reviews();ended=w.get('session',s['id']);self.assertEqual(ended['status'],'review_failed');self.assertEqual(ended['messages'],s['messages'])
    def test_plan_count_and_optional_fields_do_not_discard_valid_grades(self):
        for mode in ('next-long','next-text','next-empty','optional-missing'):
            with self.subTest(mode=mode):
                Provider.mode='ok';s=self.send(self.begin());Provider.mode=mode;done=self.review(s);r=done['review'];self.assertEqual(r['score'],59)
                if mode=='next-long':self.assertEqual(len(r['next']),4);self.assertEqual(len(r['additionalNext']),2)
                if mode=='next-text':self.assertEqual(r['next'],['先说结论','给出证据'])
                if mode=='next-empty':self.assertEqual(r['next'],['测试调整措施']);self.assertEqual(r['nextSource'],'loss-actions')
                if mode=='optional-missing':self.assertEqual(r['next'],[]);self.assertEqual(r['translations'][0]['source'],'conversation')
    def test_review_accepts_model_prose_objects_lists_and_long_examples(self):
        for mode in ('structured-improved','long-improved'):
            with self.subTest(mode=mode):
                Provider.mode='ok';s=self.send(self.begin());Provider.mode=mode;s=self.review(s)
                self.assertEqual(s['status'],'reviewed');self.assertEqual(s['review']['score'],59)
                improved=s['review']['timeline'][0]['improved']
                if mode=='long-improved':self.assertTrue(improved.endswith('完整长示范末尾。'));self.assertGreater(len(improved),12000)
                else:self.assertIn('明确当前判断',improved);self.assertIn('证据还需具体',s['review']['timeline'][0]['feedback'])
    def test_missing_example_supplemented_by_model_without_regrading(self):
        s=self.send(self.begin());Provider.mode='empty-improved';s=self.review(s)
        self.assertEqual(s['review']['score'],59);self.assertEqual(s['review']['detailStatus'],'completed')
        self.assertIn('模型替身补全示范',s['review']['timeline'][0]['improved'])
        self.assertEqual(sum('分析完整记录' in c['body']['messages'][0]['content'] for c in Provider.calls),1)
    def test_missing_example_failure_retains_grades_then_retry_only_details(self):
        s=self.send(self.begin());Provider.mode='details-fail';s=self.review(s)
        self.assertEqual(s['status'],'reviewed');self.assertEqual(s['review']['detailStatus'],'partial')
        self.assertEqual(s['review']['timeline'][0]['improved'],'')
        before=copy.deepcopy(s);calls=len(Provider.calls);Provider.mode='ok'
        s=self.call('review-details',sessionId=s['id'],revision=s['revision'])
        self.assertEqual(s['review']['detailStatus'],'completed');self.assertEqual(s['messages'],before['messages'])
        self.assertEqual(s['review']['dims'],before['review']['dims']);self.assertEqual(s['review']['score'],before['review']['score'])
        self.assertEqual(s['review']['timeline'][0]['dims'],before['review']['timeline'][0]['dims'])
        self.assertEqual(len(Provider.calls),calls+1)
    def test_quotes_analysis_saved_frozen_referenced_and_stale(self):
        raw='先把测试条件说清楚。\n需要我做什么决定？'
        self.call('object-quotes',objectId='builtin-project',quotes=raw)
        result=self.call('analyze-object',objectId='builtin-project')
        self.assertEqual(result['sampleCount'],2);self.assertEqual(result['traits'][0]['evidence'],[raw.splitlines()[0]])
        s=self.begin();self.assertEqual(s['object']['quotes'],raw);self.assertIn('quoteAnalysis',s['object'])
        prompt=Provider.calls[-1]['body']['messages'][0]['content'];self.assertIn('模拟而非对象说过的原话',prompt)
        before=copy.deepcopy(s['object'])
        self.call('object-quotes',objectId='builtin-project',quotes='更新后的语录。')
        current=next(o for o in w.objects() if o['id']=='builtin-project')
        self.assertTrue(current['quoteAnalysisStale']);self.assertNotIn('quoteAnalysis',current)
        self.assertEqual(w.get('session',s['id'])['object'],before)
        w.init(server.ROOT,server.DATA_ROOT,server.CONFIG_PATH,server)
        self.assertEqual(next(o for o in w.objects() if o['id']=='builtin-project')['quotes'],'更新后的语录。')
    def test_quote_analysis_rejects_invented_evidence_and_empty_input(self):
        self.call('object-quotes',objectId='builtin-project',quotes='真实记录的语录。');Provider.mode='quote-bad-evidence'
        with self.assertRaises(urllib.error.HTTPError):self.call('analyze-object',objectId='builtin-project')
        self.assertIsNone(w.get('object-analysis','builtin-project'))
        self.assertEqual(w.get('object','builtin-project')['quotes'],'真实记录的语录。')
        self.call('object-quotes',objectId='builtin-project',quotes='')
        with self.assertRaises(urllib.error.HTTPError):self.call('analyze-object',objectId='builtin-project')
    def test_no_empty_config_overwrites_existing(self):
        self.assertFalse(self.call('import-config',config={'apis':[]})['imported'])
        self.assertEqual(w.config_store()['active'],'p1')

if __name__=='__main__':unittest.main(verbosity=2)
