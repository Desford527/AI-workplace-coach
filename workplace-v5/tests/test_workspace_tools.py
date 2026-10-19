"""Behavioral tests for bounded AI edits, atomicity, and library snapshots."""
import copy
import json
import pathlib
import sys
import urllib.error
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from test_workflow import Workflow
import workplace as w
import workspace_tools as wt

# Reuse the HTTP harness without inheriting all baseline test methods.
import unittest
class WorkspaceTools(unittest.TestCase):
    setUpClass=classmethod(Workflow.setUpClass.__func__)
    tearDownClass=classmethod(Workflow.tearDownClass.__func__)
    setUp=Workflow.setUp
    tearDown=Workflow.tearDown
    call=Workflow.call
    begin=Workflow.begin
    send=Workflow.send
    review=Workflow.review
    def test_ai_create_preserves_roster_config_and_forms(self):
        old=copy.deepcopy(w.objects());cfg=w.config_store()
        r=self.call('free-command',text='我想新增一个对象，王工是测试负责人')
        self.assertIn('新建对象：王工',r['changes'])
        created=next(o for o in w.objects() if o['name']=='王工')
        self.assertTrue(all(created.get(k) for k in ('goals','standards','style','facts','inferences','boundaries')))
        self.assertEqual(len(w.objects()),len(old)+1);self.assertEqual(w.config_store(),cfg)
        created['goals']='表单继续可用';self.call('object',object=created)
        self.assertEqual(next(o for o in w.objects() if o['id']==created['id'])['goals'],'表单继续可用')
    def test_multi_intent_preserves_original_and_freezes_new_context(self):
        s=self.begin();snapshot=copy.deepcopy(s['object']);cfg=w.config_store()
        r=self.call('free-command',text='我觉得朱总重视风险，今天说：“先把没验证的条件讲清楚，再谈交付。”增加追问强度；收录一条汇报延期的经验。',sessionId=s['id'],revision=s['revision'])
        self.assertEqual(len(r['changes']),4);self.assertEqual(r['session']['intensity'],'深入')
        self.assertEqual(r['session']['object'],snapshot);self.assertEqual(r['session']['messages'],s['messages'])
        self.assertEqual(r['session']['revision'],s['revision']+1)
        obj=next(o for o in w.objects() if o['id']==snapshot['id'])
        self.assertIn(snapshot['personality'],obj['personality']);self.assertIn('先把没验证的条件讲清楚，再谈交付。',obj['quotes'])
        self.assertEqual(w.config_store(),cfg)
        new=self.call('start',sceneId='progress',objectId=obj['id'])
        self.assertEqual(new['intensity'],'深入');self.assertEqual(new['object'],obj)
        self.assertIn('汇报延期（测试替身）',[e['title'] for e in new['experiences']])
        source=copy.deepcopy(new['experiences']);self.call('import-experiences',entries=[{'title':'新经验','content':'更新内容'}])
        self.assertEqual(w.get('session',new['id'])['experiences'],source)
    def test_invalid_multi_operations_are_atomic(self):
        for value in ('非法计划','伪造语录','禁止操作'):
            before=copy.deepcopy(w.objects());prefs=wt.preferences()
            with self.assertRaises(urllib.error.HTTPError):self.call('free-command',text=value)
            self.assertEqual(w.objects(),before);self.assertEqual(wt.preferences(),prefs);self.assertEqual(w.all_docs('command'),[])
    def test_clarification_and_followup(self):
        before=copy.deepcopy(w.objects())
        r=self.call('free-command',text='模糊对象，更重视验证')
        self.assertTrue(r['clarification']);self.assertEqual(r['changes'],[]);self.assertEqual(w.objects(),before)
        result=self.call('free-command',text='是朱总',previousId=r['id'])
        self.assertEqual(result['clarification'],'');self.assertIn('补充画像',result['changes'][0])
    def test_import_deduplicates_and_rejects_whole_invalid_batch(self):
        self.assertEqual(self.call('import-experiences',entries=wt.experiences())['added'],0)
        entries=[{'title':'核实边界','category':'技术评审','content':'先核实条件，再提出判断。'}]
        self.assertEqual(self.call('import-experiences',entries=entries)['added'],1)
        self.assertEqual(self.call('import-experiences',entries=entries)['skipped'],1)
        count=len(wt.experiences())
        with self.assertRaises(urllib.error.HTTPError):self.call('import-experiences',entries=[{'title':'本不应写入','content':'正文'},{'title':'缺少正文'}])
        self.assertEqual(len(wt.experiences()),count)
        w.init(w.ROOT,w.DATA.parent,w.CONFIG,w.LEGACY)
        self.assertIn('核实边界',[e['title'] for e in wt.experiences()])
    def test_failed_provider_keeps_input_and_no_mutation(self):
        from fake_provider import Provider
        Provider.mode='payment';before=copy.deepcopy(w.objects())
        with self.assertRaises(urllib.error.HTTPError):self.call('free-command',text='新增一个对象王工')
        self.assertEqual(w.objects(),before);self.assertEqual(w.all_docs('command'),[])
    def test_finished_session_is_not_modified_and_stale_active_rejected(self):
        s=self.begin()
        with self.assertRaises(urllib.error.HTTPError) as cm:self.call('free-command',text='增加追问强度',sessionId=s['id'],revision=-1)
        self.assertEqual(cm.exception.code,409)
        s=self.call('cancel',sessionId=s['id'],revision=s['revision']);before=copy.deepcopy(s)
        r=self.call('free-command',text='增加追问强度',sessionId=s['id'],revision=s['revision'])
        self.assertNotIn('session',r);self.assertEqual(w.get('session',s['id']),before)
    def test_idempotent_command_does_not_duplicate_append(self):
        import uuid
        rid=str(uuid.uuid4());data={'requestId':rid,'text':'我觉得朱总更重视风险'}
        first=self.call('free-command',**data);roster=copy.deepcopy(w.objects())
        self.assertEqual(self.call('free-command',**data),first);self.assertEqual(w.objects(),roster)

del Workflow
if __name__=='__main__':unittest.main()
