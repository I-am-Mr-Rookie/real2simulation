import json
from Build.reports.compile import compile_all
from tests.reports.fixture import synthetic_fitter_result, synthetic_report
F=synthetic_fitter_result()
res=compile_all(lambda t:synthetic_report(F,t), F, 'evidence/S17/compiled')
open('evidence/S17/compile_manifest.json','w').write(json.dumps(res,indent=1,sort_keys=True))
print({t:(e['status'],e.get('pages'),e.get('reason')) for t,e in res.items()})
