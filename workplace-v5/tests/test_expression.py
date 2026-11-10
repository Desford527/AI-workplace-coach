"""Audience selection, protocol failure and no collateral workspace writes."""
import copy,json,unittest,urllib.error
import test_workflow as harness
from fake_provider import Provider
import workplace as w
class Expression(unittest.TestCase):
    setUpClass=classmethod(harness.Workflow.setUpClass.__func__)
    tearDownClass=classmethod(harness.Workflow.tearDownClass.__func__)
    setUp=harness.Workflow.setUp
    tearDown=harness.Workflow.tearDown
    call=harness.Workflow.call
    def test_existing_object_and_no_mutation(self):
        objects=copy.deepcopy(w.objects());config=copy.deepcopy(w.config_store())
        r=self.call('optimize-expression',text='我觉得我同事脑子有问题',objectId='builtin-project',goal='请协助协调')
        self.assertEqual(r['object']['id'],'builtin-project');self.assertIn('协作',r['professional'])
        self.assertEqual(w.objects(),objects);self.assertEqual(w.config_store(),config);self.assertEqual(w.all_docs('session'),[])
        payload=json.loads(Provider.calls[-1]['body']['messages'][-1]['content'])
        self.assertEqual(payload['original'],'我觉得我同事脑子有问题');self.assertEqual(payload['audience']['name'],r['object']['name'])
        self.assertNotIn('apiKey',payload)
    def test_general_object_with_empty_roster(self):
        for o in w.objects():self.call('delete-object',objectId=o['id'])
        r=self.call('optimize-expression',text='这个需求不合理',objectId='general',language='en')
        self.assertEqual(r['object']['id'],'general')
        self.assertIn('使用英文',Provider.calls[-1]['body']['messages'][0]['content'])
    def test_deleted_target_and_input_limits(self):
        for data in [dict(text=''),dict(text='x',objectId='missing'),dict(text='x',language='fr'),dict(text='x',context='x'*4001)]:
            with self.assertRaises(urllib.error.HTTPError):self.call('optimize-expression',**data)
        self.assertEqual(Provider.calls,[])
    def test_invalid_model_and_payment_do_not_write(self):
        for mode in ['expression-invalid','payment']:
            Provider.mode=mode
            with self.assertRaises(urllib.error.HTTPError):self.call('optimize-expression',text='希望明确分工')
            self.assertEqual(w.all_docs('session'),[])
