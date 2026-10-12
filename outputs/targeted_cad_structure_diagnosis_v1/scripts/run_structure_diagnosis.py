from structure_common import *
import sys,shutil,subprocess,time,traceback,argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
import trimesh,cadquery as cq
from residual_features import analyze,emit,grid,iou
from validate_native_parametric_cad import code_audit,validate
from metric_runtime import evaluate

def worker(job_path):
 job=read(job_path);d=Path(job_path).parent;row=job['row'];source=trimesh.load(O/'cases'/row['case_id']/'source/part_local.ply',force='mesh',process=True);code=(d/'cad.py').read_text();audit=code_audit(code);dump(d/'static_representation.json',audit)
 if not audit['safe_grammar']:raise ValueError('Representation gate failed: '+repr(audit['unsupported_reasons']))
 scope={};exec(compile(code,'cad.py','exec'),scope);shape=scope['result'].val()
 if not shape.isValid() or not shape.Solids():raise ValueError('Invalid native solid')
 cq.exporters.export(shape,str(d/'cad.step'));rep=validate(d/'cad.py',d/'cad.step',O/'cases'/row['case_id']/'source/part_local.ply',d/'validation');dump(d/'representation.json',rep)
 if rep['classification']!='A_NATIVE_PARAMETRIC' or not rep['self_contained'] or rep['mesh_wrapper_detected']:raise ValueError('Native isolated representation gate failed')
 shape=cq.importers.importStep(str(d/'cad.step')).val();v,f=shape.tessellate(.001,.05);cm=trimesh.Trimesh([x.toTuple() for x in v],f,process=True);cm.export(d/'cad_mesh.ply');cm=trimesh.load(d/'cad_mesh.ply',force='mesh',process=True)
 points=np.load(O/'cases'/row['case_id']/'source/frozen_evaluation_points.npy');metrics=evaluate(source,cm,row['seed'],source_points=points);dump(d/'metrics.json',metrics);dump(d/'record.json',{'metrics':metrics,'status':status(metrics),'representation_pass':True,'step_reload_pass':True,'code_sha256':sha(d/'cad.py'),'step_sha256':sha(d/'cad.step')})

def pilot(row):
 start=time.time();d=O/'cases'/row['case_id']
 if (d/'result.json').exists():return read(d/'result.json')
 source=trimesh.load(d/'source/part_local.ply',force='mesh',process=True);current=d/'baseline';before=row['metrics'];m=before;attempts=[];accepted=[];stop='MAX_ROUNDS';basecode=(current/'cad.py').read_text()
 # Validate cache against unchanged baseline metrics before any feature trial.
 baseline_mesh=trimesh.load(current/'cad_mesh.ply',force='mesh',process=True);check=evaluate(source,baseline_mesh,row['seed'],source_points=np.load(d/'source/frozen_evaluation_points.npy'));drift={k:check[k]-before[k] for k in ['iou','normalized_chamfer','bbox_error','centroid_l2_error']};dump(d/'baseline/evaluator_drift.json',drift);assert max(map(abs,drift.values()))<1e-10,drift
 for rnd in range(1,4):
  rd=d/'rounds'/f'round_{rnd}';rd.mkdir(exist_ok=True);cad=trimesh.load(current/'cad_mesh.ply',force='mesh',process=True);code=(current/'cad.py').read_text();res,_=analyze(source,cad,code,rd/'residual.npz');dump(rd/'residual.json',res)
  assert abs(res['iou']-m['iou'])<1e-12,(res['iou'],m['iou'])
  proposals=res['proposals']
  if not proposals:stop='NO_COMPACT_RULE_SUPPORTED_FEATURE';break
  results=[]
  for j,p in enumerate(proposals):
   a=rd/f'candidate_{j:02d}';a.mkdir(exist_ok=True);dump(a/'job.json',{'row':row,'feature':p});(a/'cad.py').write_text(code+'\n'+emit(p,rnd));rec={'round':rnd,'candidate':j,'feature_type':p['feature_type'],'feature_subtype':p['feature_subtype'],'path':str(a),'proposal':p,'accepted':False,'before_metrics':m,'before_features':feature_list(code)}
   if not (a/'record.json').exists():
    try:
     proc=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--worker',str(a/'job.json')],capture_output=True,text=True,timeout=180,env=os.environ.copy());(a/'execution.log').write_text(proc.stdout+'\n'+proc.stderr)
     if proc.returncode:raise RuntimeError(proc.stderr[-1600:])
    except Exception as e:dump(a/'record.json',{'error':str(e),'representation_pass':False})
   rec.update(read(a/'record.json'))
   if 'metrics' in rec:
    mm=rec['metrics'];di=mm['iou']-m['iou'];dn=mm['normalized_chamfer']-m['normalized_chamfer'];newstrict=mm['strict_pass'] and not m['strict_pass'];rec.update(delta_iou=di,delta_ncd=dn,feature_gate_pass=bool(di>=.02 or dn<=-.002 or newstrict),status_not_damaged=ORDER[status(mm)]<=ORDER[status(m)],after_features=feature_list((a/'cad.py').read_text()))
    # IoU priority, plus status and non-degrading surface quality guardrails.
    rec['eligible']=rec['feature_gate_pass'] and rec['status_not_damaged'] and di>=-1e-6 and dn<=.0005
   else:rec.update(feature_gate_pass=False,eligible=False)
   results.append(rec)
  good=[r for r in results if r['eligible']]
  if not good:attempts+=results;stop='NO_CANDIDATE_PASSES_FEATURE_ACCEPTANCE';break
  best=max(good,key=lambda r:(r['metrics']['strict_pass'],r['metrics']['iou'],-r['metrics']['normalized_chamfer'],-r['metrics']['centroid_l2_error'],-r['metrics']['bbox_error']));best['accepted']=True;attempts+=results;accepted.append(best);current=Path(best['path']);m=best['metrics']
  if m['strict_pass']:stop='STRICT_REACHED';break
 for f in ['cad.py','cad.step','cad_mesh.ply','representation.json']:shutil.copyfile(current/f,d/'final'/f)
 dump(d/'final/metrics.json',m);di=m['iou']-before['iou'];dn=m['normalized_chamfer']-before['normalized_chamfer'];improved=ORDER[status(m)]<ORDER[row['status']];out={'case_id':row['case_id'],'cohort':row['cohort'],'family':row['family'],'size_class':row['size_class'],'before_status':row['status'],'after_status':status(m),'before_metrics':before,'after_metrics':m,'delta_iou':di,'delta_ncd':dn,'new_strict':status(m)=='STRICT_ACCEPT' and row['status']!='STRICT_ACCEPT','new_near':status(m)=='NEAR_PASS' and row['status']=='REJECT','significant':bool(di>=.05 or dn<=-.003 or improved),'feature_accepted_n':len(accepted),'attempts':attempts,'stop_reason':stop,'baseline_features':feature_list(basecode),'final_features':feature_list((d/'final/cad.py').read_text()),'seconds':time.time()-start};dump(d/'result.json',out);print(json.dumps({k:out[k] for k in ['case_id','after_status','delta_iou','delta_ncd','feature_accepted_n','stop_reason']}),flush=True);return out

class RemoveCuts(ast.NodeTransformer):
 def visit_Call(self,node):
  node=self.generic_visit(node)
  return node.func.value if isinstance(node.func,ast.Attribute) and node.func.attr=='cut' else node

def audit(row):
 d=O/'audits'/row['case_id'];d.mkdir(parents=True,exist_ok=True)
 if (d/'diagnosis.json').exists():return read(d/'diagnosis.json')
 old=V/'cases'/row['case_id'];source=trimesh.load(old/'source/part_local.ply',force='mesh',process=True);cad=trimesh.load(old/'cad/cad_mesh.ply',force='mesh',process=True);code=(old/'cad/cad.py').read_text();res,(a,b,origin,pitch)=analyze(source,cad,code,propose=False);assert abs(res['iou']-row['metrics']['iou'])<1e-12
 out={**row,'residual':res,'current_features':feature_list(code),'diagnosis_confidence':'RULE_BASED_NOT_SEMANTIC_GROUND_TRUTH'}
 if row['family']=='D_EXTRUDE_WITH_CUTS':
  basecode=ast.unparse(RemoveCuts().visit(ast.parse(code)))+'\n';scope={};assert code_audit(basecode)['safe_grammar'];exec(compile(basecode,'base_body.py','exec'),scope);shape=scope['result'].val();v,f=shape.tessellate(.001,.05);base=trimesh.Trimesh([x.toTuple() for x in v],f,process=True)
  from fit_logic import voxel_occupancy
  # Same shared grid; audit base extends only within original bounds for subtractive construction.
  bo=voxel_occupancy(base,origin,pitch,a.shape);cutmask=bo&~b;removed=int(cutmask.sum());truecut=int((cutmask&~a).sum());falsecut=int((cutmask&a).sum());sourceoutside=int((a&~bo).sum())/max(1,int(a.sum()));extra=bo&~a
  cc,_=__import__('residual_features').components(extra,origin,pitch,base,source);totalextra=int(extra.sum());largest=max((c['voxel_n'] for c in cc),default=0)/max(1,totalextra)
  # A compact local cut can repair an otherwise covering base. Broad distributed residue cannot establish that claim.
  base_iou=iou(a,bo);basecorrect=sourceoutside<=.03 and (base_iou>=.85 or (base_iou>=.7 and len([c for c in cc if c['voxel_n']>=16])<=3 and largest>=.65))
  out.update(base_body_status='BASE_BODY_CORRECT' if basecorrect else 'BASE_BODY_WRONG',base_body_rule='outside_source_fraction<=.03 and (baseIoU>=.85 or baseIoU>=.7 with <=3 compact major residual components)',base_iou=base_iou,source_outside_base_fraction=sourceoutside,cut_removed_voxel_n=removed,cut_removed_fraction=removed/max(1,int(bo.sum())),cut_correct_voxel_n=truecut,cut_wrong_voxel_n=falsecut,cut_precision=truecut/max(1,removed),wrong_cut_parameter=bool(falsecut>max(16,.1*removed)),cuts_below_voxel_resolution=removed<16)
  out['primary_diagnosis']='BASE_BODY_WRONG' if not basecorrect else 'WRONG_CUT_PARAMETER' if out['wrong_cut_parameter'] else 'MISSING_OR_INCORRECT_LOCAL_CUT' if row['status']!='STRICT_ACCEPT' else 'STRICT_ACCEPTED'
  out['wrong_profile']=not basecorrect;out['wrong_family']='UNCONFIRMED';(d/'base_without_cuts.py').write_text(basecode)
 else:
  # Failure of a box/cylinder fit alone does not prove family misclassification.
  m=row['metrics'];missing=res['missing_voxel_n'];extra=res['extra_voxel_n'];tot=max(1,res['source_voxel_n']);major=[c for c in res['missing_components']+res['extra_components'] if c['voxel_n']>=max(16,.01*tot)]
  if m['strict_pass'] or (m['iou']>=.9 and m['normalized_chamfer']<=.012):new='TRUE_SIMPLE_PRIMITIVE';confidence=.8;reason='High geometric agreement with actual native single primitive; remaining gate failures do not establish a different family'
  elif major and max(c['voxel_n'] for c in major)/tot<=.25 and len(major)<=4 and m['iou']>=.7:
   new='BOOLEAN_COMPOSITION' if missing>extra else 'BOX_WITH_RECESS' if out['current_features'].get('box') else 'CYLINDER_WITH_HOLE';confidence=.55;reason='Localized occupancy residual supports a secondary add/cut hypothesis; type remains provisional until feature trial'
  else:new='UNRESOLVED_BASE_OR_PROFILE';confidence=.25;reason='Broad residual cannot distinguish family error, axis/size error, or open-mesh occupancy ambiguity without a tested alternative'
  out.update(old_family=row['family'],new_family=new,confidence=confidence,reason=reason,misclassified=new not in ['TRUE_SIMPLE_PRIMITIVE','UNRESOLVED_BASE_OR_PROFILE'],classification_verified=False)
 dump(d/'diagnosis.json',out);print('AUDIT',row['case_id'],row['family'],flush=True);return out

if __name__=='__main__':
 if '--worker' in sys.argv:worker(sys.argv[sys.argv.index('--worker')+1]);raise SystemExit
 p=argparse.ArgumentParser();p.add_argument('--phase',choices=['audit','pilot'],required=True);p.add_argument('--workers',type=int,default=12);p.add_argument('--limit',type=int);args=p.parse_args()
 rows=read(O/'manifests/subset.json') if args.phase=='pilot' else [r for r in read(O/'manifests/all_parts.json') if r['family'] in ['A_SIMPLE_PRIMITIVE','D_EXTRUDE_WITH_CUTS']];rows=rows[:args.limit] if args.limit else rows;errors=[]
 with ProcessPoolExecutor(max_workers=args.workers) as pool:
  fs={pool.submit(pilot if args.phase=='pilot' else audit,r):r['case_id'] for r in rows}
  for f in as_completed(fs):
   try:f.result()
   except Exception as e:errors.append({'case_id':fs[f],'error':str(e),'traceback':traceback.format_exc()});print('ERROR',errors[-1],flush=True)
 dump(O/'logs'/f'{args.phase}_errors.json',errors)
 if errors:raise SystemExit(1)
 print('COMPLETE',args.phase,len(rows),flush=True)
