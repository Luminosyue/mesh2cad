import json, numpy as np, torch
from pathlib import Path
REPO=Path('/data/home/cuiyuehan/project/mesh2cad'); import sys
sys.path[:0]=[str(REPO/'scripts'),str(REPO/'scripts'/'geometry_pack_v1')]
from spatiallm_curve_token_c2_frozen_v2.export_curve_tokens import curve_inputs,load_backbone
C2=REPO/'ours3'/'curve_encoder_scale_curvature_v1'/'runs'/'C2_frozen_v1'/'best.pt'; enc,_=load_backbone(C2,torch.device('cuda')); enc.eval()
for case in ['airplane','wheel','kettle','toaster','irregular_highpoly']:
 root=REPO/'ours3'/'p1_batch_run'/case; parts=json.loads((root/'parts.json').read_text())['parts']
 for p in parts:
  d=root/'packs'/p; s=np.load(d/'surface_points.npy'); xyz=s[:,:3]; c=xyz.mean(0); _,_,vh=np.linalg.svd(xyz-c,full_matrices=False); axis=vh[0]; t=np.linspace(-1,1,32); curve=c+t[:,None]*(xyz-c).dot(axis).min() * axis
  # robust principal extent
  proj=(xyz-c).dot(axis); curve=c+np.linspace(proj.min(),proj.max(),32)[:,None]*axis
  tan=np.gradient(curve,axis=0); tan/=np.maximum(np.linalg.norm(tan,axis=1,keepdims=True),1e-8)
  f,sc=curve_inputs(curve,tan.astype('float32'))
  with torch.no_grad(): tok=enc(torch.from_numpy(f[None]).cuda(),torch.from_numpy(sc[None]).cuda())['token'].float().cpu().numpy()
  np.save(d/'curve_tokens.npy',tok.astype('float32')); (d/'curve_diagnostics.json').write_text(json.dumps({'type':'PCA_LINE','n_curves':1,'source':'mesh_surface_pca'},indent=2)); meta=json.loads((d/'prepare_summary.json').read_text()); meta.update({'empty_sharp_fallback':None,'n_curve_tokens':1,'curve_source':'generic_pca_axis'}); (d/'prepare_summary.json').write_text(json.dumps(meta,indent=2))
 print(case,len(parts))
