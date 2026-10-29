# Differential check: workspace parseJob verdict must equal integration.schema.json (Draft 2020-12) verdict.
import json, subprocess, sys
from jsonschema import Draft202012Validator
schema = json.load(open('Build/web/src/shell/integration.schema.json'))
job_schema = {**schema, 'oneOf': [{'$ref': '#/$defs/job'}]}
ok = {'contract_version':'1.0.0','kind':'job','job_id':'j1','revision':0,'status':'queued','result':None,'error':None}
scene = {'scene_id':'s1','scene_version':'1.0.0','access':'private','evidence':'synthetic'}
err = {'code':'PROCESSING_FAILED','message':'x'}
c = [ok, {**ok,'status':'running'}, {**ok,'status':'ready','result':scene}, {**ok,'status':'failed','error':err}, {**ok,'status':'cancelled'},
     {**ok,'status':'ready'}, {**ok,'status':'ready','result':scene,'error':err}, {**ok,'status':'failed'}, {**ok,'result':scene}, {**ok,'error':err},
     {**ok,'revision':-1}, {**ok,'revision':1.5}, {**ok,'status':'done'}, {**ok,'job_id':'../x'}, {**ok,'job_id':''}, {**ok,'extra':1}, {**ok,'kind':'viewer'},
     {**ok,'contract_version':'2.0.0'}, {**ok,'status':'ready','result':{**scene,'evidence':'real'}}, {**ok,'status':'ready','result':{**scene,'scene_version':'2'}},
     {**ok,'status':'failed','error':{'code':'BOOM','message':'x'}}, {**ok,'status':'failed','error':{'code':'NOT_FOUND','message':''}},
     {**ok,'status':'failed','error':{'code':'NOT_FOUND','message':'y'*241}}, {k:v for k,v in ok.items() if k!='error'},
     {**ok,'status':'ready','result':{**scene,'x':1}}, {**ok,'status':'failed','error':{**err,'x':1}}, {**ok,'status':'ready','result':{**scene,'access':'x'}}]
js = "import {parseJob} from './Build/web/src/workspace/workflow.mjs';const c=JSON.parse(process.argv[1]);console.log(JSON.stringify(c.map(x=>parseJob(x)!==null)))"
got = json.loads(subprocess.check_output(['node','--input-type=module','-e',js,json.dumps(c)]))
want = [Draft202012Validator(job_schema).is_valid(x) for x in c]
bad = [i for i,(a,b) in enumerate(zip(got,want)) if a!=b]
print(json.dumps({'cases':len(c),'valid_per_schema':sum(want),'mismatch_indexes':bad}))
sys.exit(1 if bad else 0)

