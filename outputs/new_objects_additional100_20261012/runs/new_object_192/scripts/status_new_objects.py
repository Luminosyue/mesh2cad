from pathlib import Path
import json,datetime
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/new_objects_additional100_20261012/runs/new_object_192')
rows=[]
for d in sorted((O/'objects').glob('new_object_*')):
 log=O/'logs'/(d.name+'_xpart.log')
 lines=log.read_text(errors='replace').splitlines() if log.exists() else []
 stages=[s for s in lines if '[xpart_from_p3]' in s or 'Error' in s or 'Traceback' in s]
 rows.append({'object':d.name,'completed_meshes':len(list((d/'xpart_parts').glob('*/complete*.obj'))),'cad_steps':len(list((d/'xpart_parts_cadquery_features').glob('*/*.step'))),'cad_jobs_done':len(list((d/'xpart_parts_cadquery_features').glob('*/job_status.json'))),'metrics_done':len(list((d/'xpart_parts_cadquery_features').glob('*/current_protocol_metrics.json'))),'stage':stages[-1] if stages else 'Waiting/loading','log_tail':lines[-1][-180:] if lines else '', 'run_status':json.loads((d/'run_status.json').read_text()).get('status') if (d/'run_status.json').exists() else 'RUNNING'})
print(json.dumps({'time':str(datetime.datetime.now()),'rows':rows},indent=2),flush=True)
