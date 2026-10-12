from v2_common import *
import sys,time,shutil,subprocess,argparse,traceback
from concurrent.futures import ProcessPoolExecutor,as_completed
import trimesh,cadquery as cq
from metric_runtime import evaluate
from native_geometry import proposals,optimize_candidate,family,profile_types
from validate_native_parametric_cad import code_audit,validate as native_validate
ORDER={'STRICT_ACCEPT':0,'NEAR_PASS':1,'REJECT':2}

def candidate_worker(job_path,row_path,destination):
 dest=Path(destination);job=read(job_path);row=read(row_path);d=O/'cases'/row['case_id'];code=job['code'];audit=code_audit(code)
 if not audit['safe_grammar']:raise ValueError('Representation static gate: '+repr(audit['unsupported_reasons']))
 m=trimesh.load(d/'source/part_local.ply',force='mesh',process=True);points=np.load(d/'source/frozen_evaluation_points.npy');scope={};exec(compile(code,'geometry_proposal.py','exec'),scope);shape=scope['result'].val()
 if not shape.isValid() or not shape.Solids():raise ValueError('Initial native prototype is invalid')
 vv,ff=shape.tessellate(.001,.05);cm=trimesh.Trimesh([v.toTuple() for v in vv],ff,process=True)
 fitted,opt=optimize_candidate(m,cm,code,points,row['seed']);dump(dest/'optimization.json',opt);(dest/'initial_code.py').write_text(code);(dest/'cad.py').write_text(fitted)
 audit=code_audit(fitted)
 if not audit['safe_grammar']:raise ValueError('Optimized representation static gate failed')
 scope={};exec(compile(fitted,'cad.py','exec'),scope);shape=scope['result'].val()
 if not shape.isValid() or not shape.Solids():raise ValueError('Optimized CAD invalid')
 cq.exporters.export(shape,str(dest/'cad.step'));representation=native_validate(dest/'cad.py',dest/'cad.step',d/'source/part_local.ply',dest/'validation');dump(dest/'representation.json',representation)
 if not (representation['classification']=='A_NATIVE_PARAMETRIC' and representation['self_contained'] and not representation['mesh_wrapper_detected']):raise ValueError('Representation gate rejects candidate: '+repr(representation['reasons']))
 # Evaluation tessellation is unchanged and is separate from Render V4.
 loaded=cq.importers.importStep(str(dest/'cad.step')).val();vv,ff=loaded.tessellate(.001,.05);cm=trimesh.Trimesh([v.toTuple() for v in vv],ff,process=True);cm.export(dest/'cad_mesh.ply');cm=trimesh.load(dest/'cad_mesh.ply',force='mesh',process=True);metrics=evaluate(m,cm,row['seed']);params={'profile_fits':job['parameters'],'local_optimization':{k:v for k,v in opt.items() if k!='steps'}};dump(dest/'parameters.json',params)
 r={'kind':job['kind'],'family':family(fitted),'profile_types':profile_types(fitted),'path':str(dest),'metrics':metrics,'score':score(metrics),'status':status(metrics),'parameters':params,'representation_classification':representation['classification'],'self_contained':True,'execution':{'parse_pass':True,'execute_pass':True,'step_reload_pass':True},'new_candidate':True,'evaluation_mesh_serialized':True};dump(dest/'record.json',r)

def run(row):
 d=O/'cases'/row['case_id'];rp=d/'result.json'
 if rp.exists():return read(rp)
 t=time.time();assert shutil.disk_usage(O).free>5*2**30;m=trimesh.load(d/'source/part_local.ply',force='mesh',process=True);cm=trimesh.load(d/'baseline/cad_mesh.ply',force='mesh',process=True);code=(d/'baseline/cad.py').read_text();metrics=evaluate(m,cm,row['seed']);drift={k:metrics[k]-row['baseline_metrics'][k] for k in ['iou','normalized_chamfer','bbox_error','centroid_l2_error']};assert max(map(abs,drift.values()))<1e-10,drift
 base={'candidate_id':0,'kind':'PRESERVED_'+row['baseline_version'],'family':family(code),'profile_types':profile_types(code),'path':str(d/'baseline'),'metrics':metrics,'score':score(metrics),'status':status(metrics),'parameters':read(d/'baseline/parameters.json'),'representation_classification':'A_NATIVE_PARAMETRIC','self_contained':True,'new_candidate':False,'baseline_drift':drift,'execution':{'parse_pass':True,'execute_pass':True,'step_reload_pass':True,'inherited_audit_hash_verified':True}}
 plan=d/'optimization/proposals.json'
 if plan.exists():plans=read(plan);jobs=plans['jobs'];diagnosis=plans['diagnosis']
 else:jobs,diagnosis=proposals(row,m,code,read(d/'source/features_v2.json'));dump(plan,{'jobs':jobs,'diagnosis':diagnosis})
 dump(d/'diagnosis/diagnosis.json',diagnosis);dump(d/'source/row.json',row);attempts=[base]
 for i,job in enumerate(jobs,1):
  dest=d/'candidates'/f'candidate_{i:02d}';dest.mkdir(exist_ok=True);record=dest/'record.json';dump(dest/'proposal.json',job)
  if not record.exists():
   try:
    p=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--candidate',str(dest/'proposal.json'),str(d/'source/row.json'),str(dest)],capture_output=True,text=True,timeout=300,env=os.environ.copy());(dest/'execution.log').write_text(p.stdout+'\n'+p.stderr)
    if p.returncode!=0:raise ValueError('Candidate process failed: '+p.stderr[-1500:])
   except Exception as e:dump(record,{'candidate_id':i,'kind':job['kind'],'family':job['family'],'path':str(dest),'error':str(e),'new_candidate':True})
  rec=read(record);rec['candidate_id']=i;attempts.append(rec)
 valid=[a for a in attempts if 'metrics' in a];best=min(valid,key=lambda a:(ORDER[a['status']],a['score']));bd=Path(best['path'])
 for f in ['cad.py','cad.step','cad_mesh.ply','parameters.json']:shutil.copyfile(bd/f,d/'cad'/f)
 rep=read(bd/'representation.json');dump(d/'cad/representation.json',rep);dump(d/'metrics/metrics.json',best['metrics'])
 v1=read(d/'source/v1_result.json');out={**row,'status':best['status'],'metrics':best['metrics'],'score':best['score'],'family':best['family'],'profile_types':best['profile_types'],'fix_type':best['kind'],'selected_candidate':best['candidate_id'],'attempts':attempts,'v1_metrics':v1['metrics'],'new_strict_vs_baseline':best['status']=='STRICT_ACCEPT' and row['baseline_status']!='STRICT_ACCEPT','source_sha256':sha(d/'source/part_local.ply'),'elapsed_seconds':time.time()-t,'fitting_performed':True};dump(rp,out);print(json.dumps({'case':row['case_id'],'status':out['status'],'new_strict':out['new_strict_vs_baseline'],'fix':out['fix_type'],'iou':round(out['metrics']['iou'],5),'seconds':round(out['elapsed_seconds'],1)}),flush=True);return out

def near_gate(rows):
 near=[r for r in rows if r['v1_status']=='NEAR_PASS'];results=[read(O/'cases'/r['case_id']/'result.json') for r in near];counts={s:sum(r['status']==s for r in results) for s in ORDER};extra=sum(r['new_strict_vs_baseline'] for r in results);pass_gate=counts['STRICT_ACCEPT']>=10 and extra>=1 and counts['REJECT']==0;gate={'near_input_n':63,'near_to_strict_n':counts['STRICT_ACCEPT'],'near_still_near_n':counts['NEAR_PASS'],'near_to_reject_n':counts['REJECT'],'rescue_rate':counts['STRICT_ACCEPT']/63,'new_strict_vs_baseline_n':extra,'inherited_baseline_strict_n':sum(r['baseline_status']=='STRICT_ACCEPT' for r in near),'reject_stage_allowed':pass_gate,'decision':'PROCEED_REJECT' if pass_gate else 'PAUSE_REJECT_AND_ANALYZE_PROFILE_FAMILY_OPTIMIZATION'};dump(O/'reports/NEAR_GATE.json',gate);print(json.dumps(gate),flush=True);return gate
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='--candidate':candidate_worker(*sys.argv[2:5]);raise SystemExit
 ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['near','reject'],required=True);ap.add_argument('--limit',type=int);ap.add_argument('--workers',type=int,default=12);a=ap.parse_args();rows=read(O/'manifests/cases.json')
 if a.phase=='reject':assert read(O/'reports/NEAR_GATE.json')['reject_stage_allowed'],'Near rescue pause gate blocks reject fitting'
 group=[r for r in rows if r['v1_status']==('NEAR_PASS' if a.phase=='near' else 'REJECT')];group=sorted(group,key=lambda r:score(r['baseline_metrics']));group=group[:a.limit] if a.limit else group;errors=[]
 with ProcessPoolExecutor(max_workers=a.workers) as pool:
  futures={pool.submit(run,r):r['case_id'] for r in group}
  for future in as_completed(futures):
   try:future.result()
   except Exception as e:errors.append({'case':futures[future],'error':str(e),'traceback':traceback.format_exc()});print('CASE_FAILED',futures[future],str(e),flush=True)
 dump(O/'logs'/f'{a.phase}_failures.json',errors)
 if errors:raise SystemExit(1)
 if a.phase=='near' and not a.limit:near_gate(rows)
 print('PHASE_COMPLETE',a.phase,len(group),flush=True)
