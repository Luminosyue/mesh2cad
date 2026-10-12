import os,sys,json
from pathlib import Path
import numpy as np,torch
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); sys.path[:0]=[str(ROOT/'SpatialLM'),str(ROOT/'scripts'),str(ROOT/'scripts/geometry_pack_v1'),str(ROOT/'scripts/separate_edge_tokens_v1')]
os.environ['CUDA_VISIBLE_DEVICES']='7'
from separate_edge_tokens_v1.common import make_plugin,load_model
from geometry_pack_v1.decode_joint_j0_j2 import _load_surface_only
ck=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b0/best_model'; model,tok=load_model(ck,separate_edge=False,device='cuda',dtype=torch.float32,freeze_sonata=True); model.eval(); plugin=make_plugin(separate_edge=False)
rows=[]
for p in sorted((ROOT/'ours3/p1_cadquery_tank_airplane54_full_v1/assets/XPart/geometry_pack_v1').glob('airplane__PART_*')):
 surf=_load_surface_only(plugin,p/'surface_points.npy'); s=surf[0].to(model.device); st,_=model.forward_geometry(s,None,device=model.device,dtype=next(model.parameters()).dtype)
 rows.append({'PART_ID':p.name.split('__')[1],'SURFACE_INPUT_POINT_N':int(s.shape[0]),'SURFACE_CONDITIONING_TOKEN_N':int(st.shape[1]),'CURVE_INPUT_TOKEN_N':int(np.load(p/'curve_tokens.npy').shape[0]),'CURVE_CONDITIONING_TOKEN_N':int(np.load(p/'curve_tokens.npy').shape[0]),'OTHER_CONDITIONING_TOKEN_N':0}); print(rows[-1],flush=True)
json.dump(rows,open(ROOT/'ours3/airplane_fullseq_14bit_ir_v1_cond.json','w'),indent=2)
