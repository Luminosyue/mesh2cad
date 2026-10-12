from rebuild_cases import ROOT,RUN
import json,collections
p=json.loads((RUN/'progress.json').read_text());print('BATCH',p['completed'],p['total'],p['counts'])
v=[];fails=[]
for case,pid in json.loads((RUN/'task_manifest.json').read_text())['tasks']:
    d=ROOT/case/'xpart_parts_cadquery_features'/pid
    f=d/'rebuild_validation.json'
    if f.exists():
        r=json.loads(f.read_text());v.append(r['status'])
        if r['status']!='VERIFIED':fails.append((case,pid,r['status'],(d/'validation.log').read_text()[-600:]))
print('VALIDATION',dict(collections.Counter(v)));print('VALIDATION_ISSUES',json.dumps(fails))
print('RECONSTRUCTION_FAILURES',[(r['case'],r['part'],r.get('termination')) for r in p['results'] if r['status']=='FAILED'])
if (RUN/'assembly_progress.json').exists():
    a=json.loads((RUN/'assembly_progress.json').read_text());print('ASSEMBLY',len(a),[r for r in a if r['status']!='DONE'])
