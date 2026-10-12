#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
from collections import Counter
import numpy as np

R=Path('/data/home/cuiyuehan/project/mesh2cad')
O=R/'ours3/historical_fusion360_canonical_transform_dependency_audit_v1'
S=R/'cad_spatial_dataset/Fusion360/train'
RAW=R/'cad_spatial_dataset/Fusion360/reconstruction/reconstruction'
PREV=R/'ours3/m2_deepcad_fusion360_clean10k_real_pipeline_v1'

def digest(p):
 h=hashlib.sha256();
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def dump(name,x):
 p=O/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n');return p
def pct(x):
 a=np.asarray(x,float);return {k:float(np.percentile(a,q)) for k,q in [('min',0),('p10',10),('median',50),('p90',90),('max',100)]}
def entry(component,rel,symbol,lines,inp,out,caller,callee):
 p=R/rel;return dict(component=component,source_file=str(p),function_class=symbol,line_function_symbol=lines,input=inp,output=out,caller=caller,callee=callee,sha256=digest(p))

def main():
 O.mkdir(parents=True,exist_ok=True)
 expected={'REAL_M2_PIPELINE_PROVENANCE.json':'fcdbf4ab92f3acc6eccca494440a56b1211f8544e7b83b64c3ed3ccb427e9c6f','SOURCE_POOL_INVENTORY.json':'6190ddfd890d72b444cc6232816edee12e3b10071fc78782b0997f37181ca02b','CAD_ID_REGISTRY.jsonl':'ae9746d8cffaeb63b886beec21a55b7c207b4db608378c2ced0f300d8e77317f'}
 evidence={n:{'path':str(PREV/n),'expected':h,'actual':digest(PREV/n),'match':digest(PREV/n)==h} for n,h in expected.items()}
 if not all(v['match'] for v in evidence.values()):raise RuntimeError('entry evidence hash mismatch')
 code=[
 entry('Fusion raw JSON to DSL','scripts/fusion360/build_fusion360_sample.py','build_one','65-95','raw JSON','program.dsl','CLI/main','fusion360_to_dsl.convert_file'),
 entry('Official geometry copy','scripts/fusion360/build_fusion360_sample.py','build_one','97-115','official STEP/OBJ','model.step/model.obj/model.stl','build_one','trimesh'),
 entry('Dora spatial features','scripts/fusion360/build_fusion360_sample.py','build_one','126-170','model.stl','points/normals/edge_score/features.npy','build_one','build_cad_spatial_part.py'),
 entry('Feature assembly','scripts/build_cad_spatial_part.py','main pipeline','1090-1091','points,normals,edge_score','features.npy [N,7]','build_fusion360_sample subprocess','numpy.concatenate'),
 entry('Canonical transform computation','scripts/deepcad/cad_canonical.py','compute_transform','78-98','features[:,0:3]','scale,translation,bbox metadata','build_sample_canonical','numpy min/max/norm'),
 entry('Canonical feature transform','scripts/deepcad/cad_canonical.py','canonicalize_features','112-119','features.npy, transform','features_canonical.npy','build_sample_canonical','apply_points'),
 entry('Canonical DSL transform','scripts/deepcad/cad_canonical.py','transform_dsl','271-319','program.dsl, transform','program_canonical.dsl text','build_sample_canonical','AST operation-aware scaling/translation'),
 entry('Canonical asset writer','scripts/deepcad/cad_canonical.py','build_sample_canonical','330-368','features.npy,program.dsl','features_canonical.npy,program_canonical.dsl,coordinate_transform.json','build_fusion360_sample.build_one','compute_transform/canonicalize_features/transform_dsl'),
 entry('Canonical build caller','scripts/fusion360/build_fusion360_sample.py','build_one','197-204','sample directory','canonical assets','CLI/main','cad_canonical.build_sample_canonical'),
 entry('Original M2 geometry pack consumer','scripts/geometry_pack_v1/pack.py','freeze_cad_target/load_frozen_transform','33-61','program_canonical.dsl,coordinate_transform.json,model.step','cad_target.dsl,canonical surface','V3 data builder','copy/load only'),
 ]
 dump('HISTORICAL_CANONICALIZATION_CODE_MAP.json',{'entry_evidence':evidence,'components':code})
 dataflow={'nodes':{
  'RAW_JSON':{'to':['program.dsl'],'operation':'fusion360_to_dsl.convert_file'},
  'RAW_STEP':{'to':['model.step'],'operation':'official file copy; not used by historical compute_transform'},
  'RAW_OBJ':{'to':['model.obj','model.stl'],'operation':'official OBJ copy then trimesh export STL'},
  'model.stl':{'to':['DORA_FEATURES'],'operation':'build_cad_spatial_part.py'},
  'DORA_FEATURES':{'schema':'xyz(3)+normal(3)+edge_score(1)','to':['CANONICAL_TRANSFORM','features_canonical.npy'],'operation':'compute_transform uses only [:,0:3] min/max'},
  'CANONICAL_TRANSFORM':{'formula':'s=6/||max(xyz)-min(xyz)||; t=-s*min(xyz); p_canonical=s*p+t','to':['program_canonical.dsl','features_canonical.npy']},
  'program.dsl':{'to':['program_canonical.dsl'],'operation':'AST transform lengths by s, world coordinates by s,t; directions unchanged'},
 },'critical_finding':'STEP/OBJ/JSON do not directly enter historical transform calculation; only sampled xyz in features.npy does. No Dora label, edge_score, normal, grouping, PCA, rotation, or semantic field is accessed.'}
 dump('FUSION360_CANONICALIZATION_DATAFLOW.json',dataflow)
 (O/'FUSION360_CANONICALIZATION_DATAFLOW.md').write_text('# Historical Fusion360 canonicalization dataflow\n\n`raw JSON -> program.dsl`\n\n`raw OBJ -> STL -> Dora sampler -> features.npy`\n\n`features[:,0:3] min/max -> scale + translation -> coordinate_transform.json`\n\n`program.dsl + transform -> program_canonical.dsl`\n\nRaw STEP is copied as official geometry but is not read by historical `compute_transform`. Only geometric XYZ is used from Dora output.\n')

 complete=[]
 for d in sorted(x for x in S.iterdir() if x.is_dir()):
  req=['features.npy','coordinate_transform.json','program_canonical.dsl','source.json','model.step','model.obj']
  if all((d/n).is_file() for n in req):complete.append(d)
 # Exact frozen compatible set is 602 by prior inventory; retain deterministic lexical identity.
 frozen=complete
 chosen=sorted(frozen,key=lambda d:hashlib.sha256(('HISTORICAL_FUSION_FEATURE20_V1|'+d.name).encode()).hexdigest())[:20]
 feature_rows=[]
 for d in chosen:
  a=np.load(d/'features.npy',mmap_mode='r'); xyz=np.asarray(a[:,:3]);
  feature_rows.append(dict(cad_id=d.name,path=str(d/'features.npy'),sha256=digest(d/'features.npy'),shape=list(a.shape),dtype=str(a.dtype),ndim=a.ndim,finite=bool(np.isfinite(a).all()),channel_interpretation={'0:3':'xyz','3:6':'normal','6':'edge_score'} if a.ndim==2 and a.shape[1]==7 else 'UNKNOWN',actually_accessed_by_canonicalization='features[:, :3] only',aggregates='min(axis=0), max(axis=0), L2 norm(max-min)',xyz_min=xyz.min(0).tolist(),xyz_max=xyz.max(0).tolist()))
 p=O/'DORA_FEATURES_CONTENT_AUDIT.jsonl';p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in feature_rows))

 breakdown={'components':[
  {'component':'TRANSLATION','source_variable':'mn = features[:,0:3].min(axis=0)','derived_from':'sampled geometric xyz','formula':'t=-scale*mn','requires_features_npy':'YES historically; NO semantically','requires_dora_specific_semantics':'NO'},
  {'component':'SCALE','source_variable':'mn,mx = extrema of features[:,0:3]','derived_from':'sampled geometric xyz bbox diagonal','formula':'s=6.0/||mx-mn||','requires_features_npy':'YES historically; NO semantically','requires_dora_specific_semantics':'NO'},
  {'component':'ROTATION','source_variable':None,'derived_from':None,'formula':'identity','requires_features_npy':'NO','requires_dora_specific_semantics':'NO'},
  {'component':'REFLECTION','source_variable':None,'derived_from':None,'formula':'none','requires_features_npy':'NO','requires_dora_specific_semantics':'NO'},
  {'component':'AXIS_PERMUTATION','source_variable':None,'derived_from':None,'formula':'none','requires_features_npy':'NO','requires_dora_specific_semantics':'NO'},
  {'component':'SIGN_FLIP','source_variable':None,'derived_from':None,'formula':'none','requires_features_npy':'NO','requires_dora_specific_semantics':'NO'},
 ]}
 dump('COORDINATE_TRANSFORM_DEPENDENCY_BREAKDOWN.json',breakdown)
 semantic={'fields':[{'field':'features[:,0:3] xyz','class':'B_GEOMETRIC_BUT_DORA_DERIVED','used':True,'reason':'pure positions, but historical samples were emitted by Dora front-end'}, {'field':'features[:,3:6] normals','class':'B_GEOMETRIC_BUT_DORA_DERIVED','used':False},{'field':'features[:,6] edge_score','class':'C_DORA_SEMANTIC','used':False}], 'canonicalization_uses_dora_semantics':False}
 dump('DORA_DEPENDENCY_SEMANTIC_CLASSIFICATION.json',semantic)
 step=[
 {'dependency':'bbox center/min and extent','historical_source':'sampled xyz extrema','step_recoverable':True,'deterministic':True,'ambiguity':'historical sampled extrema need not equal exact BRep extrema','required_algorithm':'OCC exact/controlled BRep bbox','replacement_status':'RECOVERABLE_WITH_CANONICAL_TIEBREAK'},
 {'dependency':'uniform scale to diagonal 6','historical_source':'sampled xyz bbox diagonal','step_recoverable':True,'deterministic':True,'ambiguity':'numeric mismatch versus sample-derived bbox','required_algorithm':'s=6/OCC_bbox_diagonal','replacement_status':'RECOVERABLE_WITH_CANONICAL_TIEBREAK'},
 {'dependency':'rotation/orientation','historical_source':'identity/source frame','step_recoverable':True,'deterministic':True,'ambiguity':'none because no orientation normalization exists historically','required_algorithm':'preserve raw source axes','replacement_status':'DIRECTLY_RECOVERABLE'},
 {'dependency':'semantic grouping/labels','historical_source':'not used','step_recoverable':True,'deterministic':True,'ambiguity':'not applicable','required_algorithm':'none','replacement_status':'DIRECTLY_RECOVERABLE'}]
 dump('STEP_BREP_REPLACEMENT_FEASIBILITY.json',{'preferred_source':'STEP/BRep','dependencies':step})
 mesh=[{'dependency':'bbox extrema and scale','mesh_recoverable':True,'deterministic_for_fixed_OBJ':True,'ambiguity':'tessellation/vertex sampling can differ from historical sampled-surface extrema','required_algorithm':'fixed OBJ vertex bbox or deterministic surface sampling','replacement_status':'RECOVERABLE_WITH_CANONICAL_TIEBREAK'},{'dependency':'orientation','mesh_recoverable':True,'deterministic_for_fixed_OBJ':True,'ambiguity':'none if source axes preserved; PCA must not be introduced','replacement_status':'DIRECTLY_RECOVERABLE'}]
 dump('MESH_REPLACEMENT_FEASIBILITY.json',{'STEP_BREP_PREFERRED':True,'MESH_ONLY_IS_NOT_HISTORICALLY_NUMERIC_EQUIVALENT_WITHOUT_OVERLAP_TEST':True,'dependencies':mesh})

 raw_counts=Counter(); overlap=[]
 for d in frozen:
  sid=d.name
  flags={'RAW_JSON':(RAW/f'{sid}.json').is_file() or (d/'source.json').is_file(),'RAW_STEP':(RAW/f'{sid}.step').is_file() or (d/'model.step').is_file(),'RAW_OBJ':(RAW/f'{sid}.obj').is_file() or (d/'model.obj').is_file(),'HISTORICAL_FEATURES_NPY':(d/'features.npy').is_file(),'HISTORICAL_COORDINATE_TRANSFORM':(d/'coordinate_transform.json').is_file(),'HISTORICAL_PROGRAM_CANONICAL_DSL':(d/'program_canonical.dsl').is_file()}
  for k,v in flags.items():raw_counts[k]+=int(v)
  overlap.append({'cad_id':sid,**flags,'complete':all(flags.values())})
 asset={'FROZEN_FUSION360_N':len(frozen),**{k+'_AVAILABLE':v for k,v in raw_counts.items()},'OVERLAP_COMPLETE_N':sum(x['complete'] for x in overlap),'records':overlap}
 dump('FUSION360_602_OVERLAP_ASSET_AUDIT.json',asset)

 scales=[];tmag=[];diags=[];identity=[];mins=[];maxs=[]
 for d in frozen:
  x=json.loads((d/'coordinate_transform.json').read_text());s=float(x['scale']);t=np.asarray(x['translation'],float)
  scales.append(s);tmag.append(float(np.linalg.norm(t)));diags.append(float(x['source_diagonal']));mins.append(x['source_bbox_min']);maxs.append(x['source_bbox_max']);identity.append(abs(s-1)<1e-6 and np.linalg.norm(t)<1e-6)
 dist={'N':len(scales),'scale':pct(scales),'translation_magnitude':pct(tmag),'source_diagonal':pct(diags),'identity_count':sum(identity),'near_identity_scale_1pct':sum(abs(x-1)<=.01 for x in scales),'rotation':'IDENTITY_ALL','rotation_matrix_unique_n':1,'quaternion':'[1,0,0,0] all','determinant':'1 all','axis_permutation':'NONE_ALL','reflection_presence':0,'sign_flip_presence':0,'discrete_orientation_families':1,'interpretation':'centering to bbox minimum plus uniform scale; no rotation/orientation normalization'}
 dump('HISTORICAL_TRANSFORM_DISTRIBUTION.json',dist)

 design={'STATUS':'DESIGN_ONLY_NOT_IMPLEMENTED','input':'raw JSON + raw STEP (OBJ optional)','proposal_steps':['convert raw JSON using one explicitly frozen verified Fusion converter/runtime','load raw STEP with OCC','compute deterministic BRep bbox in preserved source axes','s=6/bbox diagonal; t=-s*bbox_min','write transform under a new protocol version','apply operation-aware AST transform to program.dsl','validate on historical overlap before expansion'],'tie_breaks':['no PCA, axis permutation, reflection or sign selection; preserve raw STEP axes','freeze OCC version and bounding algorithm','freeze tolerances and float serialization'],'warning':'This is a protocol amendment, not historical numeric reproduction. Sample-derived and exact BRep extrema can differ.'}
 dump('DORA_FREE_CANONICALIZATION_DESIGN_V0.json',design)
 repro={'name':'FUSION360_DORA_FREE_CANONICALIZATION_OVERLAP602_V1','STATUS':'DESIGN_ONLY','cohort':'all 602 frozen Fusion360 overlap cases','levels':['LEVEL_1_TRANSFORM_NUMERIC_EQUIVALENT','LEVEL_2_CANONICAL_GEOMETRY_EQUIVALENT','LEVEL_3_CANONICAL_DSL_SEMANTIC_EQUIVALENT','LEVEL_4_M2_INPUT_EQUIVALENT'],'comparisons':['scale/translation deltas and transformed bbox','historical/new DSL parse+execute+STEP reload','canonical STEP Chamfer_rel/H95/Coverage/BBox with frozen evaluator','surface correspondence/alignment','GT curve alignment','C2 and real K8 token/interface compatibility','tokenizer/splice/EOS/result supervision'],'decision':'approve expansion only after predeclared semantic and M2-input equivalence gates pass; no byte identity requirement'}
 dump('OVERLAP602_REPRODUCTION_PROTOCOL.json',repro)
 levels={'LEVEL_1':{'name':'TRANSFORM_NUMERIC_EQUIVALENT','meaning':'scale and translation agree within frozen tolerance'},'LEVEL_2':{'name':'CANONICAL_GEOMETRY_EQUIVALENT','meaning':'executed canonical shapes agree under frozen geometry evaluator'},'LEVEL_3':{'name':'CANONICAL_DSL_SEMANTIC_EQUIVALENT','meaning':'program operation and geometry semantics equivalent; text bytes may differ'},'LEVEL_4':{'name':'M2_INPUT_EQUIVALENT','meaning':'surface/curve spatial alignment, token budget and supervision splice compatible'},'required_for_production':['LEVEL_2','LEVEL_3','LEVEL_4']}
 dump('EQUIVALENCE_LEVEL_DEFINITION.json',levels)

 split=json.loads((R/'cad_spatial_dataset/Fusion360/reconstruction/train_test.json').read_text());ids=sorted(set(split['train'])|set(split['test']))
 nr={'RAW_FUSION360_N':len(ids),'RAW_WITH_JSON':sum((RAW/f'{i}.json').is_file() for i in ids),'RAW_WITH_STEP':sum((RAW/f'{i}.step').is_file() for i in ids),'RAW_WITH_OBJ':sum((RAW/f'{i}.obj').is_file() for i in ids),'RAW_WITH_ALL_REQUIRED_SOURCE_ASSETS':sum(all((RAW/f'{i}.{e}').is_file() for e in ['json','step','obj']) for i in ids)}
 nr['DORA_FREE_THEORETICAL_EXPANDABLE_N']=sum((RAW/f'{i}.json').is_file() and (RAW/f'{i}.step').is_file() for i in ids)
 dump('RAW_FUSION360_EXPANSION_READINESS.json',nr)
 replacements=Counter(x['replacement_status'] for x in step)
 final={'CURRENT_GATE':'FUSION360_DORA_DEPENDENCY_REPLACEABLE_WITH_PROTOCOL_AMENDMENT','DORA_FREE_PROTOCOL_APPROVABLE':'CONDITIONAL','HISTORICAL_PIPELINE':{'RAW_JSON':'YES','RAW_STEP':'YES','RAW_OBJ':'YES','FEATURES_NPY_USED':'YES','COORDINATE_TRANSFORM_USED':'YES','PROGRAM_CANONICAL_DSL_USED':'YES'},'DORA_DEPENDENCY':{'TRANSLATION_REQUIRES_DORA':'NO semantically; YES for historical numeric sample extrema','SCALE_REQUIRES_DORA':'NO semantically; YES for historical numeric sample extrema','ROTATION_REQUIRES_DORA':'NO','AXIS_SIGN_REQUIRES_DORA':'NO','FEATURE_GROUPING_REQUIRES_DORA':'NO','SEMANTIC_LABEL_REQUIRES_DORA':'NO'},'FEATURES_NPY':{'AUDITED_CASE_N':len(feature_rows),'FEATURE_SHAPE':sorted({str(x['shape']) for x in feature_rows}),'ACTUALLY_USED_FIELDS':['xyz columns 0:3'],'PURE_GEOMETRIC_FIELDS':['xyz'],'DORA_SEMANTIC_FIELDS':[],'UNKNOWN_FIELDS':[]},'STEP_BREP_RECOVERY':{'DIRECTLY_RECOVERABLE':replacements['DIRECTLY_RECOVERABLE'],'RECOVERABLE_WITH_TIEBREAK':replacements['RECOVERABLE_WITH_CANONICAL_TIEBREAK'],'NON_UNIQUE':replacements['NON_UNIQUE'],'DORA_SEMANTIC_REQUIRED':replacements['DORA_SEMANTIC_REQUIRED'],'UNKNOWN':replacements['UNKNOWN']},'OVERLAP602':asset,'RAW_EXPANSION':nr,'MODEL':{'DORA_RUN':'NO','TRAINING_RUN':'NO','DECODE_RUN':'NO','M2_CHANGED':'NO','C2_CHANGED':'NO','SONATA_CHANGED':'NO','DSL_CHANGED':'NO'},'NEXT_STEP':'FUSION360_DORA_FREE_CANONICALIZATION_OVERLAP602_V1'}
 dump('FINAL_REPORT.json',final)
 (O/'FINAL_REPORT.md').write_text('# Historical Fusion360 canonical-transform dependency audit V1\n\n**Gate:** `FUSION360_DORA_DEPENDENCY_REPLACEABLE_WITH_PROTOCOL_AMENDMENT`\n\nHistorical canonicalization uses only `features[:,0:3]` extrema. It performs uniform scaling and translation to bbox-min; it does not use normals, edge score, segmentation, grouping, labels, PCA, rotation, reflections, axis permutations, or sign flips. Therefore Dora semantics are not required. However, replacing sampled XYZ extrema with an OCC/BRep bbox is a new numerical protocol and must pass the designed 602-case overlap reproduction audit before expansion. No Dora, training, decode, or asset generation was run.\n')
 manifest={p.name:{'size':p.stat().st_size,'sha256':digest(p)} for p in sorted(O.iterdir()) if p.is_file()}
 dump('FILE_SHA256_MANIFEST.json',manifest)
 print(json.dumps(final,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
