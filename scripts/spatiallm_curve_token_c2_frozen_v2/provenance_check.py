"""Independent 20-CAD direct-C2 versus on-disk exporter provenance check."""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, subprocess, sys
import numpy as np, torch

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0,str(ROOT/'scripts'))
from curve_encoder_baseline_v1.dataset import _normalized_s
from curve_encoder_scale_curvature_v1.config import EXPERIMENTS, TYPE_TO_ID
from curve_encoder_scale_curvature_v1.dataset import curve_local_frame
from curve_encoder_scale_curvature_v1.models import build_model

CKPT=ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'
OLD_MANIFEST=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b1_budget_postencoder_phase1_v2_100/runs/run1/MANIFEST.json'
OCC={0:'LINE',1:'CIRCLE',2:'ELLIPSE',3:'BSPLINE'}

def direct(sample,model,device):
 z=np.load(sample/'curve_samples.npz'); n=int(z['num_curves'][0]); brep=json.loads((ROOT/'cad_spatial_dataset'/('DeepCAD' if 'deepcad_train' in sample.parts else 'Fusion360')/'geometry_pack_v1'/sample.name/'brep_edges.json').read_text())
 sharp={int(e['edge_index']):bool(e.get('is_sharp',False)) for e in brep['edges']}; rows=[]
 for i in range(n):
  typ=OCC.get(int(z['curve_type_id'][i])); edge=int(z['curve_edge_id'][i])
  if typ not in TYPE_TO_ID or not sharp.get(edge,False):continue
  xyz=np.asarray(z['curve_xyz_normalized'][i],np.float64);tan=np.asarray(z['curve_tangent'][i],np.float32)
  local,_,_=curve_local_frame(xyz);s=_normalized_s(xyz.astype(np.float32),'uniform_abscissa')
  feat=np.concatenate([local,tan,s],-1).astype(np.float32);length=float(np.linalg.norm(np.diff(xyz,axis=0),axis=1).sum())
  rows.append((length,feat,np.array([np.log(length+1e-6)],np.float32)))
 order=np.argsort([-x[0] for x in rows])[:128]
 rows=[rows[int(i)] for i in order]
 with torch.no_grad():out=model(torch.from_numpy(np.stack([x[1] for x in rows])).to(device),torch.from_numpy(np.stack([x[2] for x in rows])).to(device))
 return out['token'].float().cpu().numpy().astype(np.float32)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--exporter',required=True);ap.add_argument('--output',required=True);ap.add_argument('--device',default='cuda:0');a=ap.parse_args();out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=False)
 source=json.loads(OLD_MANIFEST.read_text())['rows'][:20]; ids=[]
 for r in source:
  ds=r['dataset'];sample=pathlib.Path(r['surface_path']).parent.name; ids.append({'dataset':ds,'sample_id':sample,'cad_dir':('deepcad_train' if ds=='deepcad' else 'fusion360_train')+'/'+sample})
 (out/'ids.json').write_text(json.dumps(ids,indent=2))
 token_root=out/'tokens'
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=env.get('CUDA_VISIBLE_DEVICES','')
 subprocess.run([sys.executable,a.exporter,'--ids',str(out/'ids.json'),'--output-root',str(token_root),'--device',a.device],check=True,env=env)
 ck=torch.load(CKPT,map_location='cpu',weights_only=False);model=build_model(EXPERIMENTS['C2']);model.load_state_dict(ck['model']);model.eval().to(a.device)
 for p in model.parameters():p.requires_grad_(False)
 rows=[]
 for r in ids:
  raw=ROOT/'ours3/curve_token_data_v1'/r['cad_dir'];A=direct(raw,model,a.device);B=np.load(token_root/r['dataset']/r['sample_id']/'curve_tokens.npy')
  diff=float(np.max(np.abs(A-B))) if A.size else 0.;rows.append({'cad_id':r['dataset']+'__'+r['sample_id'],'shape':list(A.shape),'array_equal':bool(np.array_equal(A,B)),'max_abs_diff':diff})
 report={'CURVE_ENCODER_CHECKPOINT':str(CKPT.relative_to(ROOT)),'CURVE_ENCODER_CHECKPOINT_SHA256':hashlib.sha256(CKPT.read_bytes()).hexdigest(),'CURVE_ENCODER_FROZEN':all(not p.requires_grad for p in model.parameters()),'DIRECT_C2_VS_EXPORTED_TOKEN':f"{sum(x['array_equal'] for x in rows)}/{len(rows)}",'MAX_ABS_TOKEN_DIFF':max(x['max_abs_diff'] for x in rows),'rows':rows}
 report['PASS']=report['DIRECT_C2_VS_EXPORTED_TOKEN']=='20/20' and report['MAX_ABS_TOKEN_DIFF']==0 and report['CURVE_ENCODER_FROZEN']
 (out/'PROVENANCE.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));raise SystemExit(0 if report['PASS'] else 2)
if __name__=='__main__':main()
