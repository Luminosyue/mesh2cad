"""CPU/GPU read-only model probe. Stops at the Llama forward boundary; no decode/train."""
import os,sys,pathlib,json,types,copy
R=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
O=R/'cad_spatial_dataset/geometry_pack_v2_mesh2cad/budget_probe_v1'
os.environ.update(CAD_USE_SEPARATE_EDGE_TOKENS='1',CAD_SURFACE_POINTS='4096',CAD_HELDOUT_PROTOCOL='best_v2',CAD_EDGE_SOURCE='gt_sharp',CAD_EDGE_BUDGET_MATCH='0',CAD_SECOND_STREAM='edge_points',PYTHONDONTWRITEBYTECODE='1')
sys.path[:0]=[str(R/'SpatialLM'),str(R/'scripts')]
import numpy as np,torch
from spatiallm.model import spatiallm_llama as module
from spatiallm_curve_token_v1 import heldout_geometry
from spatiallm_curve_token_v1.curve_token_injector import load_curve_tokens,_forward_geometry_with_curve_tokens
from spatiallm_curve_token_v1.curve_projector import build_curve_projector
from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin
def main():
 O.mkdir(parents=True,exist_ok=False);torch.manual_seed(42)
 heldout_geometry.install()
 plugin=get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True)
 model=module.SpatialLMLlamaForCausalLM.from_pretrained(R/'SpatialLM/models/SpatialLM1.1-Llama-1B',torch_dtype=torch.bfloat16,device_map='cuda:0',local_files_only=True).eval()
 bproj=copy.deepcopy(model.point_proj);cproj=build_curve_projector(256,model.config.hidden_size).to(device='cuda',dtype=torch.bfloat16)
 original_geometry=types.MethodType(module.SpatialLMLlamaForCausalLM.forward_geometry,model)
 original_splice=module._splice_geometry;record={}
 def splice(emb,mask,regions):
  record['surface_token_count']=int(regions[0][1].shape[0]);record['auxiliary_slot_count']=int(regions[1][1].shape[0]);record['auxiliary_valid_count']=record['auxiliary_slot_count'];record['marker_token_count']=4
  return original_splice(emb,mask,regions)
 module._splice_geometry=splice
 class StopProbe(Exception):pass
 def hook(mod,args,kwargs):
  record['total_llm_input_length']=int(kwargs['inputs_embeds'].shape[1]);record['attention_mask_active_count']=int(kwargs['attention_mask'].sum().item());raise StopProbe()
 handle=model.model.register_forward_pre_hook(hook,with_kwargs=True)
 inv=json.loads((R/'cad_spatial_dataset/geometry_pack_v2_practical/_audit_stage1_v2/inventory.json').read_text())
 candidates=[r for r in inv if r['dataset']=='deepcad'];candidates.sort(key=lambda r:len(load_curve_tokens(pathlib.Path(r['pack'])/'surface_points.npy')))
 rows=[]
 for idx in np.linspace(0,len(candidates)-1,20,dtype=int):
  rec=candidates[idx];path=pathlib.Path(rec['pack'])/'surface_points.npy';surf,edge=plugin._load_cad_separate_edge(str(path));curve=load_curve_tokens(path)
  for arm in ['M2','B1_full_postencoder']:
   model.edge_proj=cproj if arm=='M2' else bproj
   model.forward_geometry=types.MethodType(_forward_geometry_with_curve_tokens,model) if arm=='M2' else original_geometry
   record.clear();record.update(cad_id=rec['cad_id'],arm=arm,input_surface_voxels=len(surf),input_edge_voxels=len(edge),curve_payload_count=len(curve),prompt='synthetic boundary probe: 2 ordinary tokens + 4 retained geometry markers; not a training prompt length')
   ids=torch.tensor([[128000,model.point_start_token_id,model.point_token_id,model.point_end_token_id,model.edge_start_token_id,model.edge_token_id,model.edge_end_token_id,1]],device='cuda')
   try:
    with torch.no_grad():model(input_ids=ids,attention_mask=torch.ones_like(ids),point_clouds=torch.tensor(surf,dtype=torch.float32).unsqueeze(0),edge_clouds=torch.tensor(curve if arm=='M2' else edge,dtype=torch.float32).unsqueeze(0))
   except StopProbe:pass
   rows.append(record.copy());print(json.dumps(record),flush=True)
   with (O/f'{len(rows):03d}.json').open('x') as f:json.dump(record,f,indent=2)
 with (O/'RESULTS.json').open('x') as f:json.dump(rows,f,indent=2)
 handle.remove()
if __name__=='__main__':main()
