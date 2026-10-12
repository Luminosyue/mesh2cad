#!/usr/bin/env python3
from __future__ import annotations

import collections
import hashlib
import importlib.util
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
CACHE = Path('/var/tmp/cuiyuehan_mesh2cad/operation_conditioned_parameter_head_v2')
OUT = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/operation_conditioned_parameter_head_v2'
OLD = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/parameter_head_oracle_v1'
ROUTING_CODE = ROOT / 'scripts/parameter_composition_routing_v2'
OLD_CODE = ROOT / 'scripts/parameter_head_oracle_v1'
EXECUTOR = ROOT / 'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
P0_CHECKPOINT = OLD / 'train800/checkpoint_final.pt'
P0_SHA256 = '2ac24248215aea415be16e3fdca7ca344e24ae25bc2d285809dc6b13f4e6c12e'
EXECUTOR_SHA256 = '53747c0a66f9758b59c783a122c8a0b6cea8074fc7c3a762a8bfc1fe2ec850de'
sys.path.insert(0, str(ROUTING_CODE)); sys.path.insert(0, str(OLD_CODE))
from typed_composition import TypedProgram  # noqa: E402
from common import DEV_MANIFEST, load_manifest, token_contract  # noqa: E402
sys.path.insert(0, str(ROOT / 'scripts/operation_conditioned_parameter_head_v2'))
from model import OperationConditionedHead  # noqa: E402
from train import Dataset, collate  # noqa: E402

ARMS = ['P1_OPQUERY_CURVE_ONLY', 'P2_OPQUERY_SURFACE_ONLY', 'P3_OPQUERY_SURFACE_CURVE']
SYSTEMS = ['GT', 'LLM', 'P0_SIMPLE_HEAD_V1', *ARMS]


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def summary(values):
    a = np.asarray(values, dtype=float)
    return {'n': len(a), 'mean': float(a.mean()) if len(a) else None, 'median': float(np.median(a)) if len(a) else None,
            'P90': float(np.percentile(a, 90)) if len(a) else None}


class TokenHead(nn.Module):
    def __init__(self, output_dim, hidden=256):
        super().__init__(); self.net = nn.Sequential(nn.LayerNorm(262), nn.Linear(262, hidden), nn.GELU(), nn.Linear(hidden, hidden), nn.GELU(), nn.Linear(hidden, output_dim))
    def forward(self, x): return self.net(x)


class ProfileAggregator(nn.Module):
    def __init__(self, hidden=256, heads=4):
        super().__init__(); self.input = nn.Sequential(nn.LayerNorm(262), nn.Linear(262, hidden)); self.query = nn.Parameter(torch.zeros(1,1,hidden)); self.attention = nn.MultiheadAttention(hidden,heads,batch_first=True); self.output=nn.Sequential(nn.LayerNorm(hidden),nn.Linear(hidden,hidden),nn.GELU())
    def forward(self,x):
        z=self.input(x).unsqueeze(0); pooled,_=self.attention(self.query.expand(1,-1,-1),z,z,need_weights=False); return self.output(pooled[:,0])[0]


class P0Heads(nn.Module):
    def __init__(self, hidden=256):
        super().__init__(); self.circle=TokenHead(7,hidden); self.extrude_aggregator=ProfileAggregator(hidden); self.extrude=nn.Sequential(nn.Linear(hidden,hidden),nn.GELU(),nn.Linear(hidden,8)); self.box_aggregator=ProfileAggregator(hidden); self.box=nn.Sequential(nn.Linear(hidden,hidden),nn.GELU(),nn.Linear(hidden,6))
    def forward(self,kind,x):
        if kind=='circle':
            r=self.circle(x[0]); return {'center':r[:3],'radius':F.softplus(r[3]),'normal':F.normalize(r[4:7],dim=0)}
        if kind=='extrude':
            r=self.extrude(self.extrude_aggregator(x)); return {'depth':r[6]}
        r=self.box(self.box_aggregator(x)); return {'origin':r[:3],'extent':torch.stack((F.softplus(r[3]),F.softplus(r[4]),r[5]))}


class P0Store:
    def __init__(self): self.cache={}
    def features(self,label):
        cad=label['cad_id']
        if cad not in self.cache:
            row={k:label[k] for k in ('target_dsl','m2_full_c2_tokens','m2_full_curves','selected_m2_indices')}; row['k_valid']=len(row['selected_m2_indices'])
            tokens,anchors,_,_=token_contract(row); self.cache[cad]=np.concatenate([tokens,anchors],axis=1).astype(np.float32)
        return torch.from_numpy(self.cache[cad][label['token_indices']])


def p0_values():
    if sha256(P0_CHECKPOINT)!=P0_SHA256: raise RuntimeError('P0 checkpoint hash mismatch')
    labels=[json.loads(x) for x in (OLD/'oracle_labels_dev.jsonl').read_text().splitlines() if x.strip()]
    ck=torch.load(P0_CHECKPOINT,map_location='cpu',weights_only=True); model=P0Heads(); model.load_state_dict(ck['model']); model.eval(); store=P0Store()
    values=collections.defaultdict(lambda:collections.defaultdict(dict))
    with torch.no_grad():
        for label in labels:
            pred=model(label['head_type'],store.features(label)); scale=float(label['object_scale']); center=np.asarray(label['object_center'])
            item=values[label['cad_id']][label['assignment']]
            if label['head_type']=='circle': item.update({'circle.center':(pred['center'].numpy()*scale+center).tolist(),'circle.radius':float(pred['radius'])*scale,'circle.normal':pred['normal'].numpy().tolist()})
            elif label['head_type']=='extrude': item['extrude.depth']=float(pred['depth'])*scale
            else:
                ext=pred['extent'].numpy()*scale; item.update({'box.origin':(pred['origin'].numpy()*scale+center).tolist(),'box.extent.width':float(ext[0]),'box.extent.depth':float(ext[1]),'box.extent.height':float(ext[2])})
    return values


def op_values(arm, rows):
    ckpath=CACHE/'training/train800'/arm/'checkpoint_final.pt'; ck=torch.load(ckpath,map_location='cpu',weights_only=True)
    model=OperationConditionedHead(arm); model.load_state_dict(ck['model']); model.eval(); data=Dataset(rows); values=collections.defaultdict(lambda:collections.defaultdict(dict))
    with torch.no_grad():
        for start in range(0,len(data),16):
            idx=range(start,min(start+16,len(data))); batch=collate(data,idx,torch.device('cpu')); pred=model(batch['query'],batch['surface'],batch['surface_padding'],batch['curve'],batch['curve_padding'])
            for j,i in enumerate(idx):
                row=rows[i]; scale=float(row['object_scale']); center=np.asarray(row['object_center']); item=values[row['cad_id']][row['assignment']]
                if row['operation_type']=='Extrude': item.update({'circle.center':(pred['circle_center'][j].numpy()*scale+center).tolist(),'circle.radius':float(pred['circle_radius'][j])*scale,'circle.normal':pred['circle_normal'][j].numpy().tolist(),'extrude.depth':float(pred['extrude_depth_one'][j])*scale})
                else:
                    ext=pred['box_extent'][j].numpy()*scale; item.update({'box.origin':(pred['box_origin'][j].numpy()*scale+center).tolist(),'box.extent.width':float(ext[0]),'box.extent.depth':float(ext[1]),'box.extent.height':float(ext[2])})
    return values,ckpath


def llm_values(text,assignments):
    p=TypedProgram(text); return {a:{s['parameter']:p.operations[a].get(s['parameter']) for s in p.operations[a].active_mask() if s['active']} for a in assignments}


def compose(gt,assignments,values):
    p=TypedProgram(gt)
    for a in assignments:
        if a in values:p.bind(a,values[a])
    return p.serialize()


def load_executor():
    if sha256(EXECUTOR)!=EXECUTOR_SHA256:raise RuntimeError('executor hash mismatch')
    spec=importlib.util.spec_from_file_location('opheadv2_executor',EXECUTOR);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m


def shape_props(s):
    q=lambda x:round(float(x),9);b=s.BoundingBox();c=[q((b.xmin+b.xmax)/2),q((b.ymin+b.ymax)/2),q((b.zmin+b.zmax)/2)];e=[q(b.xmax-b.xmin),q(b.ymax-b.ymin),q(b.zmax-b.zmin)]
    payload={'solids':len(s.Solids()),'faces':len(s.Faces()),'edges':len(s.Edges()),'bbox_center':c,'bbox_extent':e,'volume':q(s.Volume()),'area':q(s.Area()),'vertices':sorted([[q(x) for x in v.Center().toTuple()] for v in s.Vertices()]),'edge_lengths':sorted(q(x.Length()) for x in s.Edges()),'face_areas':sorted(q(x.Area()) for x in s.Faces())}
    fp=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest();return {k:v for k,v in payload.items() if k not in {'vertices','edge_lengths','face_areas'}}|{'fingerprint':fp}


def fresh(text,mesh,run,executor):
    run.mkdir(parents=True,exist_ok=False);dsl=run/'input.dsl';dsl.write_text(text);rec={'dsl_path':str(dsl),'dsl_sha256':sha256(dsl),'step_path':str(run/'result.step'),'mesh_path':str(run/'result.stl'),'parse':False,'execute':False,'brep_valid':False,'step_reload':False,'shape':None,'metrics':None,'failure':None}
    try:
        clean=executor.extract_dsl_code(text);program=executor.parse_dsl(clean);rec['parse']=True;shapes={}
        for n,node in program.assignments.items():
            if n!='result':shapes[n]=executor._build_shape(node,shapes) if isinstance(node,dict) and 'op'in node else node
        node=program.assignments['result'];result=shapes[node] if isinstance(node,str) else executor._build_shape(node,shapes);rec['execute']=True;s=result.val() if hasattr(result,'val') else result
        from OCP.BRepCheck import BRepCheck_Analyzer
        if s.wrapped.IsNull() or not BRepCheck_Analyzer(s.wrapped).IsValid():rec['failure']='INVALID';return rec
        rec['brep_valid']=True;rec['shape']=shape_props(s);import cadquery as cq;cq.exporters.export(s,rec['step_path']);loaded=cq.importers.importStep(rec['step_path']);rec['step_reload']=True;cq.exporters.export(loaded,rec['mesh_path']);rec['step_sha256']=sha256(Path(rec['step_path']));rec['mesh_sha256']=sha256(Path(rec['mesh_path']))
        import trimesh
        from scipy.spatial import cKDTree
        gt=trimesh.load(str(mesh),force='mesh');pr=trimesh.load(rec['mesh_path'],force='mesh');ge=gt.bounds[1]-gt.bounds[0];pe=pr.bounds[1]-pr.bounds[0];gc=gt.bounds.mean(0);pc=pr.bounds.mean(0);diag=max(float(np.linalg.norm(ge)),1e-12);a,_=trimesh.sample.sample_surface(gt,3000,seed=42);b,_=trimesh.sample.sample_surface(pr,3000,seed=43);da=cKDTree(b).query(a)[0];db=cKDTree(a).query(b)[0]
        rec['metrics']={'Chamfer':float((da.mean()+db.mean())/2/diag),'H95':float(np.percentile(np.r_[da,db],95)/diag),'BBox_center':float(np.linalg.norm(pc-gc)/diag),'BBox_extent':float(np.linalg.norm(pe-ge)/diag)};rec['failure']='SUCCESS'
    except Exception as e:rec['failure']=f'{type(e).__name__}: {e}'[-800:]
    return rec


def param_errors(row,pred):
    t=row['targets'];out={}
    if row['operation_type']=='Extrude':
        c=t['circle'];e=t['extrude'];out={'circle_center':float(np.linalg.norm(np.asarray(pred['circle.center'])-(np.asarray(c['center'])*row['object_scale']+row['object_center']))),'circle_radius':abs(float(pred['circle.radius'])-float(c['radius'])*row['object_scale']),'extrude_origin':float(np.linalg.norm(np.asarray(pred['circle.center'])-(np.asarray(e['origin'])*row['object_scale']+row['object_center']))),'extrude_depth':abs(float(pred['extrude.depth'])-float(e['depth'])*row['object_scale'])}
    else:
        b=t['box'];gt_o=np.asarray(b['origin'])*row['object_scale']+row['object_center'];gt_e=np.asarray(b['extent'])*row['object_scale'];out={'box_origin':float(np.linalg.norm(np.asarray(pred['box.origin'])-gt_o)),'box_extent':float(np.linalg.norm(np.asarray([pred['box.extent.width'],pred['box.extent.depth'],pred['box.extent.height']])-gt_e))}
    return out


def aggregate(rows,system,ids=None):
    x=[r[system] for r in rows if ids is None or r['cad_id'] in ids];m=lambda k:summary([r['metrics'][k] for r in x if r['metrics']])
    return {'CAD_COUNT':len(x),'STEP':sum(r['step_reload'] for r in x),'Chamfer':m('Chamfer'),'H95':m('H95'),'BBox_center':m('BBox_center'),'BBox_extent':m('BBox_extent')}


def main():
    fresh_root=OUT/'fresh_dev50';
    if fresh_root.exists():raise RuntimeError('refusing overwrite fresh_dev50')
    fresh_root.mkdir();instances=[json.loads(x) for x in (CACHE/'instances.jsonl').read_text().splitlines() if x.strip() and json.loads(x)['split']=='dev'];records=load_manifest(DEV_MANIFEST);bycad={r['cad_id']:r for r in records}
    old_occ=json.load(open(OLD/'DEV50_OCC_REPLAY.json'));assignments={r['cad_id']:r['replacement_assignments'] for r in old_occ['PER_CAD']};values={'P0_SIMPLE_HEAD_V1':p0_values()};ckpts={}
    for arm in ARMS:values[arm],ckpts[arm]=op_values(arm,instances)
    llm_by_cad={};texts={};executor=load_executor();occ=[]
    for cad in sorted(bycad):
        gt=Path(bycad[cad]['target_dsl']).read_text();old_llm=(OLD/'dev50'/cad/'LLM_PARAMETER_DSL.dsl').read_text();a=assignments.get(cad,[]);llm_by_cad[cad]=llm_values(old_llm,a) if a else {};texts={'GT':gt,'LLM':compose(gt,a,llm_by_cad[cad])}
        for system in ['P0_SIMPLE_HEAD_V1',*ARMS]:texts[system]=compose(gt,a,values[system].get(cad,{}))
        mesh=Path(bycad[cad]['target_dsl']).parent/'mesh.obj';result={'cad_id':cad,'affected':bool(a),'assignments':a}
        for system in SYSTEMS:result[system]=fresh(texts[system],mesh,fresh_root/cad/system,executor)
        occ.append(result);print(f'[dev50] {len(occ)}/50',flush=True)
    parameter=collections.defaultdict(lambda:collections.defaultdict(list))
    for row in instances:
        cad,a=row['cad_id'],row['assignment']
        if a not in assignments.get(cad,[]):continue
        for system in ['LLM','P0_SIMPLE_HEAD_V1',*ARMS]:
            pred=llm_by_cad[cad][a] if system=='LLM' else values[system][cad][a]
            for k,v in param_errors(row,pred).items():parameter[system][k].append(v)
    parameter_report={'METRICS':{s:{k:summary(v) for k,v in m.items()} for s,m in parameter.items()},'INSTANCE_COUNT':sum(len(v) for v in parameter['LLM'].values()),'OPERATION_COUNT':sum(r['assignment'] in assignments.get(r['cad_id'],[]) for r in instances),'FRESH':True}
    (OUT/'DEV50_HEAD_V2_PARAMETER_METRICS.json').write_text(json.dumps(parameter_report,indent=2)+'\n')
    (OUT/'DEV50_HEAD_V2_OCC_REPLAY.json').write_text(json.dumps({'CAD_COUNT':50,'SYSTEMS':SYSTEMS,'PER_CAD':occ,'FRESH':True},indent=2)+'\n')
    affected={r['cad_id'] for r in occ if r['affected']};common={r['cad_id'] for r in occ if r['affected'] and all(r[s]['step_reload'] and r[s]['metrics'] for s in SYSTEMS)}
    geometry={'ALL':{s:aggregate(occ,s) for s in SYSTEMS},'AFFECTED_ONLY_IDS':sorted(affected),'AFFECTED_ONLY':{s:aggregate(occ,s,affected) for s in SYSTEMS},'COMMON_VALID_AFFECTED_ONLY_IDS':sorted(common),'COMMON_VALID_AFFECTED_ONLY':{s:aggregate(occ,s,common) for s in SYSTEMS}}
    (OUT/'DEV50_HEAD_V2_GEOMETRY_METRICS.json').write_text(json.dumps(geometry,indent=2)+'\n')
    comparison={'PARAMETER_METRICS':parameter_report['METRICS'],'GEOMETRY':geometry,'P0_CHECKPOINT':str(P0_CHECKPOINT),'P0_SHA256':sha256(P0_CHECKPOINT),'ARM_CHECKPOINTS':{a:{'path':str(p),'sha256':sha256(p)} for a,p in ckpts.items()},'OLD_SIMPLE_ROUTING_V2_RESULT_USED_AS_P0':False,'ALL_SYSTEMS_FRESH_RECOMPOSED_AND_EXECUTED':True,'ANCHOR_EVAL_100_READ':False,'PILOT150_READ':False,'OFFICIAL_TEST_READ':False}
    (OUT/'LLM_VS_HEAD_V2_COMMON_VALID.json').write_text(json.dumps(comparison,indent=2)+'\n')
    print(json.dumps({'PARAMETER':parameter_report,'GEOMETRY':geometry},indent=2))


if __name__=='__main__':main()
