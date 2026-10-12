from pathlib import Path
import sys,json
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1');sys.path.insert(0,str(E/'launch'))
from a2_runtime import *
from a2_runtime import _load_sepedge
tok=AutoTokenizer.from_pretrained(str(E.parent/'p1_airplane3_exact_overfit_v1/runs/quick/checkpoint-2000'))
plugin=make_plugin(separate_edge=True)
batches=torch.load(E/'data/collated_batches.pt',weights_only=False);inv=json.loads((E/'data/block_inventory.json').read_text())
for part in json.loads((E/'data/parts.json').read_text()):
 s,e=_load_sepedge(plugin,Path(part['folder'])/'surface_points.npy');b=next(b for b,r in zip(batches,inv) if r['part']==part['part'])
 for name,v in [('point_clouds',s),('edge_clouds',e)]:
  a=b[name];print(part['part'],name,'shapes',a.shape,v.shape,'types',a.dtype,v.dtype,'nan',a.isnan().sum().item(),v.isnan().sum().item(),flush=True)
  aa=a.reshape(-1,a.shape[-1]);vv=v.reshape(-1,v.shape[-1]);aa=aa[~aa.isnan().any(-1)];vv=vv[~vv.isnan().any(-1)]
  print('valid_shapes',aa.shape,vv.shape,'equal',torch.equal(aa,vv),'maxdiff',float((aa-vv).abs().max()) if aa.shape==vv.shape else None,flush=True)
