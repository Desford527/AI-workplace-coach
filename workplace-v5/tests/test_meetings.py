"""Source attribution, deduplication, atomic selected updates and project snapshots."""
import base64
import copy
import io
import pathlib
import sys
import urllib.error
import unittest
import zipfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from test_workflow import Workflow
from fake_provider import Provider
import workplace as w
import workspace_tools as wt
import meetings

MINUTES='会议：A项目周例会\n朱总（项目负责人）：“没有验证记录，先不要承诺交付。”\n朱总要求先核实高温验证与测试条件。\n王工（测试负责人）：“我周三补齐验证记录。”\nA项目：高温验证尚未完成；王工周三补齐报告，周四确认交付计划。\n决议：先说明未验证项，再决定交付范围。'

def docx_bytes(value=MINUTES):
    from xml.sax.saxutils import escape
    buffer=io.BytesIO()
    xml='<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+''.join('<w:p><w:r><w:t>'+escape(line)+'</w:t></w:r></w:p>' for line in value.splitlines())+'</w:body></w:document>'
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as archive:archive.writestr('word/document.xml',xml)
    return buffer.getvalue()

class MeetingTests(unittest.TestCase):
    setUpClass=classmethod(Workflow.setUpClass.__func__)
    tearDownClass=classmethod(Workflow.tearDownClass.__func__)
    setUp=Workflow.setUp
    tearDown=Workflow.tearDown
    call=Workflow.call
    begin=Workflow.begin
    send=Workflow.send
    review=Workflow.review
    def analyze(self,**extra):return self.call('meeting-analyze',title='A项目周例会',text=MINUTES,**extra)
    def apply(self,m,selected=None,**extra):return self.call('meeting-apply',meetingId=m['id'],selected=selected or [i['id'] for i in m['items']],**extra)
    def test_preview_has_evidence_and_no_profile_mutation(self):
        objects=copy.deepcopy(w.objects());config=w.config_store();m=self.analyze()
        self.assertEqual(w.objects(),objects);self.assertEqual(w.config_store(),config);self.assertEqual(meetings.projects(),[])
        self.assertEqual(len(m['items']),7);self.assertEqual(m['items'][0]['objectId'],'builtin-project')
        self.assertEqual(m['items'][1]['certainty'],'inferred')
        self.assertTrue(all(q in MINUTES for item in m['items'] for q in item['evidence']))
        self.assertEqual(w.get('meeting',m['id']),m)
    def test_apply_updates_three_areas_and_preserves_frozen_training(self):
        s=self.begin();snapshot=copy.deepcopy(s);cfg=w.config_store();old=copy.deepcopy(w.objects()[0]);m=self.analyze()
        result=self.apply(m,targets={'朱总':'builtin-project','王工':'new'});self.assertEqual(result['applied'],7)
        self.assertEqual(w.get('session',s['id']),snapshot);self.assertEqual(w.config_store(),cfg)
        zh=next(o for o in w.objects() if o['id']=='builtin-project')
        self.assertIn('没有验证记录，先不要承诺交付。',zh['quotes']);self.assertTrue(zh['meetingSources'])
        self.assertIn('AI特征推测',zh['personality'])
        wang=next(o for o in w.objects() if o['name']=='王工');self.assertEqual(wang['role'],'测试负责人')
        project=meetings.projects()[0];self.assertEqual(project['name'],'A项目');self.assertIn('高温验证',project['background'])
        exp=next(e for e in wt.experiences() if e.get('meetingId'));self.assertEqual(exp['evidence'],m['items'][-1]['evidence'])
        new=self.call('start',sceneId='progress',objectId='builtin-project',projectId=project['id'])
        self.assertEqual(new['project'],project);self.assertEqual(new['background'],project['background'])
        frozen=copy.deepcopy(new);self.assertEqual(self.apply(m,targets={'王工':'new'})['applied'],0)
        self.assertEqual(len([o for o in w.objects() if o['name']=='王工']),1);self.assertEqual(w.get('session',new['id']),frozen)
        w.init(w.ROOT,w.DATA.parent,w.CONFIG,w.LEGACY);self.assertEqual(meetings.projects()[0],project)
    def test_partial_save_then_remainder_reuses_person(self):
        m=self.analyze();self.apply(m,selected=['3'],targets={'王工':'new'})
        self.assertEqual(w.get('meeting',m['id'])['status'],'partial')
        result=self.apply(m,selected=['4']);self.assertEqual(result['applied'],1)
        wang=[o for o in w.objects() if o['name']=='王工'];self.assertEqual(len(wang),1);self.assertIn('我周三补齐验证记录。',wang[0]['quotes'])
    def test_invalid_mapping_is_atomic_and_preview_retained(self):
        m=self.analyze();before=copy.deepcopy(w.objects())
        with self.assertRaises(urllib.error.HTTPError):self.apply(m,targets={'朱总':'builtin-project','王工':'missing'})
        self.assertEqual(w.objects(),before);self.assertEqual(meetings.projects(),[]);self.assertEqual(w.get('meeting',m['id'])['appliedItems'],[])
        with self.assertRaises(urllib.error.HTTPError):self.apply(m,selected=['0','5'],projectTargets={'A项目':'project-unknown'})
        self.assertEqual(w.objects(),before)
        self.call('delete-object',objectId='builtin-project')
        with self.assertRaises(urllib.error.HTTPError):self.apply(m,selected=['0'])
        self.assertNotIn('builtin-project',[o['id'] for o in w.objects()])
    def test_source_dedup_avoids_second_model_call(self):
        m=self.analyze();count=len(Provider.calls)
        again=self.call('meeting-analyze',text=MINUTES,title='另一个文件名')
        self.assertEqual(again['id'],m['id']);self.assertEqual(len(Provider.calls),count)
    def test_bad_attribution_or_model_output_does_not_save(self):
        for mode in ('meeting-bad-evidence','meeting-bad-speaker','meeting-bad-quote','meeting-bad-kind','payment'):
            Provider.mode=mode;before=copy.deepcopy(w.objects())
            with self.assertRaises(urllib.error.HTTPError):self.analyze()
            self.assertEqual(w.objects(),before);self.assertEqual(w.all_docs('meeting'),[])
    def test_file_import_utf8_gb18030_utf16_docx_and_rejection(self):
        for filename,raw in [('会议.txt',MINUTES.encode()),('会议.md',MINUTES.encode('gb18030')),('会议.txt',MINUTES.encode('utf-16')),('会议.docx',docx_bytes())]:
            parsed=self.call('meeting-file',filename=filename,data=base64.b64encode(raw).decode());self.assertEqual(parsed['text'],MINUTES)
        for filename,raw in [('会议.pdf',b'fake'),('会议.docx',b'bad zip')]:
            with self.assertRaises(urllib.error.HTTPError):self.call('meeting-file',filename=filename,data=base64.b64encode(raw).decode())
        with self.assertRaises(urllib.error.HTTPError):self.call('meeting-file',filename='会议.txt',data='not base64')
    def test_ambiguous_name_requires_mapping(self):
        other=copy.deepcopy(w.objects()[0]);other.pop('id');other['name']='朱总';self.call('object',object=other)
        m=self.analyze();self.assertEqual(m['items'][0]['objectId'],'');self.assertTrue(m['items'][0]['ambiguous'])
        with self.assertRaises(urllib.error.HTTPError):self.apply(m,selected=['0'])
    def test_project_override_used_for_model_and_new_minutes_append(self):
        m=self.analyze();self.apply(m,selected=['5']);project=meetings.projects()[0]
        s=self.call('start',sceneId='progress',objectId='builtin-project',projectId=project['id'],background='只使用已脱敏的背景')
        self.assertEqual(s['background'],'只使用已脱敏的背景')
        self.assertNotIn(project['background'],Provider.calls[-1]['body']['messages'][0]['content'])
        second=self.call('meeting-analyze',title='下一次会议',text=MINUTES+'\n新增补充记录。')
        self.apply(second,selected=['5'],projectTargets={'A项目':project['id']})
        self.assertEqual(len(meetings.projects()),1);self.assertEqual(len(meetings.projects()[0]['sources']),2)
        self.assertEqual(w.get('session',s['id'])['project'],project)
    def test_empty_extract_keeps_source_and_cannot_apply_invalid_ids(self):
        Provider.mode='meeting-empty';m=self.analyze();self.assertEqual(m['items'],[])
        self.assertEqual(m['text'],MINUTES)
        with self.assertRaises(urllib.error.HTTPError):self.apply(m,selected=['not-an-item'])

del Workflow
if __name__=='__main__':unittest.main()
