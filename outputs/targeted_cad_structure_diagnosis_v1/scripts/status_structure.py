from structure_common import *
rows=read(O/'manifests/subset.json');done=[];pending=[]
for row in rows:
 d=O/'cases'/row['case_id']
 if (d/'result.json').exists():done.append(read(d/'result.json'))
 else:
  files=list((d/'rounds').rglob('*'));files=[p for p in files if p.is_file()];latest=max(files,key=lambda p:p.stat().st_mtime) if files else None;pending.append({'case_id':row['case_id'],'latest':str(latest.relative_to(d)) if latest else None})
print(json.dumps({'completed_n':len(done),'new_strict':sum(r['new_strict'] for r in done),'significant':sum(r['significant'] for r in done),'accepted_features':sum(r['feature_accepted_n'] for r in done),'pending':pending},indent=2))
