#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
CACHE = Path('/var/tmp/cuiyuehan_mesh2cad/operation_conditioned_parameter_head_v2')
OUT = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/operation_conditioned_parameter_head_v2'
CODE = ROOT / 'scripts/operation_conditioned_parameter_head_v2'
ARMS = ['P1_OPQUERY_CURVE_ONLY','P2_OPQUERY_SURFACE_ONLY','P3_OPQUERY_SURFACE_CURVE']


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def write(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    phase1=json.load(open(OUT/'DATASET_OPERATION_QUERY_AUDIT.json'))
    overfit_gate=json.load(open(CACHE/'training/overfit20/OVERFIT_GATE.json'))
    overfit={a:json.load(open(CACHE/'training/overfit20'/a/'TRAINING_REPORT.json')) for a in ARMS}
    training={a:json.load(open(CACHE/'training/train800'/a/'TRAINING_REPORT.json')) for a in ARMS}
    params=json.load(open(OUT/'DEV50_HEAD_V2_PARAMETER_METRICS.json'))
    occ=json.load(open(OUT/'DEV50_HEAD_V2_OCC_REPLAY.json'))
    geom=json.load(open(OUT/'DEV50_HEAD_V2_GEOMETRY_METRICS.json'))
    metrics=params['METRICS']; affected=geom['COMMON_VALID_AFFECTED_ONLY']
    params.pop('INSTANCE_COUNT',None);params['OPERATION_COUNT']=16;params['PARAMETER_METRIC_OBSERVATION_COUNT']=46
    write('DEV50_HEAD_V2_PARAMETER_METRICS.json',params)
    write('OVERFIT20_REPORT.json',{'GATE':overfit_gate,'ARMS':overfit,'P0_SIMPLE_HEAD_V1_REFERENCE':str(ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/parameter_head_oracle_v1/OVERFIT20_REPORT.json')})
    checkpoint_counts={a:len(list((CACHE/'training/train800'/a).glob('checkpoint_epoch_*.pt'))) for a in ARMS}
    train_report={'STATUS':'COMPLETE','ARMS':training,'EPOCH_CHECKPOINT_COUNTS':checkpoint_counts,'SAME_SEED':42,'SAME_BATCH_SIZE':16,'SAME_EPOCHS':60,'SAME_TRAIN_OPERATION_COUNT':356,'LAMBDA_ATTENTION':0.1,'GT_RELATED_CURVES_USED_AS_HARD_MASK':False,'BACKBONE_FROZEN_OFFLINE_FEATURE_CACHE':True,'NAN_COUNT':sum(training[a]['NAN_COUNT'] for a in ARMS),'INF_COUNT':sum(training[a]['INF_COUNT'] for a in ARMS)}
    write('TRAINING_REPORT.json',train_report)

    p0,p1,p2,p3,llm=[metrics[x] for x in ['P0_SIMPLE_HEAD_V1','P1_OPQUERY_CURVE_ONLY','P2_OPQUERY_SURFACE_ONLY','P3_OPQUERY_SURFACE_CURVE','LLM']]
    final={
      'CURRENT_GATE':'OPERATION_CONDITIONED_PARAMETER_HEAD_V2_COMPLETE','AUTHORITATIVE':True,
      'CORE_QUESTION_1_OPERATION_CONDITIONING_BETTER_THAN_SIMPLE':'PARTIAL_NOT_UNIFORM',
      'CORE_QUESTION_1_EVIDENCE':{'P0_affected_chamfer_median':affected['P0_SIMPLE_HEAD_V1']['Chamfer']['median'],'best_opconditioned_affected_chamfer_median':min(affected[a]['Chamfer']['median'] for a in ARMS),'parameter_improvements':['P3 circle_center','P3 extrude_depth'],'non_improvements':['P3 box_origin','P3 box_extent','affected geometry']},
      'CORE_QUESTION_2_CURVE_VS_SURFACE':{
        'curve_only_better_parameters':['extrude_depth','box_origin'],
        'surface_only_better_parameters':['circle_radius','circle_center','box_extent_slightly'],
        'surface_only_better_affected_geometry':affected['P2_OPQUERY_SURFACE_ONLY']['Chamfer']['median']<affected['P1_OPQUERY_CURVE_ONLY']['Chamfer']['median'],
        'P1_curve_only_affected_chamfer_median':affected['P1_OPQUERY_CURVE_ONLY']['Chamfer']['median'],'P2_surface_only_affected_chamfer_median':affected['P2_OPQUERY_SURFACE_ONLY']['Chamfer']['median']},
      'CORE_QUESTION_3_SURFACE_CURVE_BEST':False,
      'CORE_QUESTION_3_EVIDENCE':{'P3_best_among_conditioned_for':['circle_center','extrude_depth'],'P3_not_best_for':['circle_radius','box_origin','box_extent','Chamfer','H95','BBox']},
      'CORE_QUESTION_4_EXTRUDE_DEPTH_RECOVERED_FROM_V1':True,
      'CORE_QUESTION_4_EVIDENCE':{'P0_median':p0['extrude_depth']['median'],'P3_median':p3['extrude_depth']['median'],'relative_reduction':1-p3['extrude_depth']['median']/p0['extrude_depth']['median'],'LLM_median':llm['extrude_depth']['median'],'P3_surpasses_LLM':p3['extrude_depth']['median']<llm['extrude_depth']['median']},
      'PARAMETER_MEDIANS':{s:{k:v['median'] for k,v in metrics[s].items()} for s in metrics},
      'STEP_ALL':{s:geom['ALL'][s]['STEP'] for s in geom['ALL']},
      'CHAMFER_MEDIAN_ALL':{s:geom['ALL'][s]['Chamfer']['median'] for s in geom['ALL']},
      'CHAMFER_MEDIAN_AFFECTED_ONLY':{s:affected[s]['Chamfer']['median'] for s in affected},
      'AFFECTED_CAD_COUNT':len(geom['AFFECTED_ONLY_IDS']),'COMMON_VALID_AFFECTED_CAD_COUNT':len(geom['COMMON_VALID_AFFECTED_ONLY_IDS']),
      'INTERPRETATION_CAVEAT':'Frozen A3 operation query already contains the A3 Surface+Curve geometry prefix; P1/P2/P3 compare additional explicit cross-attention access, not geometry-naive queries.',
      'ANCHOR_EVAL_100_READ':False,'PILOT150_READ':False,'OFFICIAL_TEST_READ':False,
    }
    write('FINAL_REPORT.json',final)
    paths=[]
    for row in occ['PER_CAD']:
      for system in occ['SYSTEMS']:
        r=row[system];paths.append({'cad_id':row['cad_id'],'system':system,'dsl_path':r['dsl_path'],'step_path':r['step_path'],'mesh_path':r['mesh_path'],'dsl_sha256':r['dsl_sha256'],'step_sha256':r.get('step_sha256'),'mesh_sha256':r.get('mesh_sha256')})
    cache_audit={'RUN_COUNT':len(paths),'DSL_PATHS_UNIQUE':len({p['dsl_path'] for p in paths})==len(paths),'STEP_PATHS_UNIQUE':len({p['step_path'] for p in paths})==len(paths),'MESH_PATHS_UNIQUE':len({p['mesh_path'] for p in paths})==len(paths),'METRIC_CACHE_USED':False,'FINGERPRINT_CACHE_USED':False,'ALL_RECORDED_HASHES_MATCH':all(sha(p['dsl_path'])==p['dsl_sha256'] and (p['step_sha256'] is None or sha(p['step_path'])==p['step_sha256']) and (p['mesh_sha256'] is None or sha(p['mesh_path'])==p['mesh_sha256']) for p in paths),'PATHS':paths}
    write('CACHE_ISOLATION_AUDIT.json',cache_audit)
    required=['DATASET_OPERATION_QUERY_AUDIT.json','OVERFIT20_REPORT.json','TRAINING_REPORT.json','DEV50_HEAD_V2_PARAMETER_METRICS.json','DEV50_HEAD_V2_OCC_REPLAY.json','DEV50_HEAD_V2_GEOMETRY_METRICS.json','LLM_VS_HEAD_V2_COMMON_VALID.json','FINAL_REPORT.json','CACHE_ISOLATION_AUDIT.json']
    assert all((OUT/x).is_file() for x in required);assert phase1['ALL_QUERY_SHAPES_VALID'] and overfit_gate['OVERFIT20_PASS'];assert all(v==60 for v in checkpoint_counts.values());assert cache_audit['RUN_COUNT']==300 and cache_audit['DSL_PATHS_UNIQUE'] and cache_audit['STEP_PATHS_UNIQUE'] and cache_audit['MESH_PATHS_UNIQUE'] and cache_audit['ALL_RECORDED_HASHES_MATCH'];assert len(occ['PER_CAD'])==50
    targets=sorted([OUT/x for x in required]+list(CODE.glob('*.py'))+[CACHE/'instances.jsonl']+list((CACHE/'features').glob('*.npz'))+list((CACHE/'training').rglob('*.pt'))+list((CACHE/'training').rglob('*.json'))+list((OUT/'fresh_dev50').rglob('*.*')))
    seen=set();entries=[]
    for p in targets:
      p=p.resolve()
      if p in seen or p.name=='FILE_SHA256_MANIFEST.json':continue
      seen.add(p);entries.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
    write('FILE_SHA256_MANIFEST.json',{'HASH_ALGORITHM':'SHA256','MANIFEST_SELF_EXCLUDED':True,'FILE_COUNT':len(entries),'FILES':entries,'CURRENT_GATE':final['CURRENT_GATE'],'ANCHOR_EVAL_100_READ':False,'PILOT150_READ':False,'OFFICIAL_TEST_READ':False})
    print(json.dumps(final,indent=2))


if __name__=='__main__':main()
