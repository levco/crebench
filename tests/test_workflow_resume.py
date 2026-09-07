import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from crebench.resume_workflow import interruption,resume_one

class CreditResumption(unittest.TestCase):
 def fixture(self,root):
  run=root/'case';attempt=run/'turn-10/attempt-1';attempt.mkdir(parents=True)
  request={'model':'anthropic/claude-opus-5','messages':[{'role':'system','content':'frozen'},{'role':'user','content':'original brief'},{'role':'assistant','content':None,'tool_calls':[{'id':'prior','function':{'name':'calculate','arguments':'{}'}}]},{'role':'tool','tool_call_id':'prior','content':'unchanged result'}],'max_tokens':49152,'stream':False,'tools':[],'tool_choice':'auto'}
  for name,obj in [('request',request),('started',{'wire_sha256':hashlib.sha256(json.dumps(request).encode()).hexdigest()}),('result',{'http_status':402})]: (attempt/(name+'.json')).write_text(json.dumps(obj))
  old={'case_id':'market-row','track':'agent','status':'infrastructure_error','requested_model':request['model'],'returned_models':[request['model']],'artifact_versions':{'workbook':1,'memo':2},'latest_workbook':None,'tool_calls':12,'elapsed_seconds':368.504,'attempts':[{'usage':{'cost':1.82}},{'http_status':402}]}
  (run/'result.json').write_text(json.dumps(old));return run,request
 def test_rejects_context_changes(self):
  with tempfile.TemporaryDirectory() as d:
   run,request=self.fixture(Path(d));p=run/'turn-10/attempt-1/request.json';request['messages'][1]['content']='answer hint';p.write_text(json.dumps(request))
   with self.assertRaisesRegex(ValueError,'wire differs'):interruption(run)
 def test_preserves_context_limits_costs_and_failed_request(self):
  with tempfile.TemporaryDirectory() as d:
   run,request=self.fixture(Path(d));prior=(run/'turn-10/attempt-1/request.json').read_bytes();seen=[]
   class Context:
    def __init__(self,*args):self.done=False;self.images=[];self.latest_workbook=None
    def call(self,name,args):self.done=True;return {'recorded':True}
   def call(req,out,turn,*args):
    seen.append((json.loads(json.dumps(req)),turn));return {'model':request['model'],'choices':[{'message':{'content':None,'tool_calls':[{'id':'finish','function':{'name':'submit_analysis','arguments':'{}'}}]}}]},[{'usage':{'cost':.2}}]
   with patch('crebench.resume_workflow.ToolContext',Context),patch('crebench.resume_workflow.model_call',call):
    r=resume_one(run,'test-token',None,{},'node')
   self.assertEqual(seen[0],(request,10));self.assertEqual(r['tool_calls'],13);self.assertEqual(r['artifact_versions'],{'workbook':1,'memo':2});self.assertEqual(r['status'],'completed')
   self.assertAlmostEqual(r['known_partial_cost_usd'],2.02);self.assertIsNone(r['gateway_reported_cost_usd']);self.assertGreaterEqual(r['elapsed_seconds'],368.504)
   self.assertEqual((run/'turn-10/attempt-1/request.json').read_bytes(),prior);self.assertTrue((run/'billing-resumption/original-result.json').exists())
