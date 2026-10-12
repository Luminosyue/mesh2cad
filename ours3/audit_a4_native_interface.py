#!/usr/bin/env python3
import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/m2_exact9998_all_curves_only_ablation_v1'
FILES=[
 ROOT/'ours3/m2_exact9998_corrected_m2_train_v1/launch/train_corrected_m2_entrypoint.py',
 ROOT/'scripts/spatiallm_curve_token_v1/train_curve_token_spatiallm.py',
 ROOT/'scripts/spatiallm_curve_token_v1/curve_token_injector.py',
 ROOT/'scripts/spatiallm_curve_token_v1/curve_projector.py',
 ROOT/'SpatialLM/spatiallm/model/spatiallm_llama.py',
 ROOT/'SpatialLM/spatiallm/tuner/data/mm_plugin.py',
 ROOT/'SpatialLM/spatiallm/tuner/data/collator.py',
 ROOT/'ours3/m2_exact9998_corrected_m2_train_v1/configs/m2_exact9998_train.yaml',
 ROOT/'ours3/m2_exact9998_surface_line_ablation_v1/configs/a1_exact9998_train.yaml',
 ROOT/'ours3/m2_exact9998_surface_nonline_ablation_v1/configs/a2_exact9998_train.yaml',
]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def inventory():
 out=[]
 for p in FILES:
  if p.is_file():
   s=p.stat();out.append({'path':str(p),'size':s.st_size,'mtime_ns':s.st_mtime_ns,'sha256':sha(p)})
  else:out.append({'path':str(p),'missing':True})
 return out
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 for d in ['configs','audits','launch','logs','runs/a4','reports']:(OUT/d).mkdir(parents=True,exist_ok=True)
 before=inventory();dump(OUT/'audits/MAIN_METHOD_SOURCE_INVENTORY_BEFORE.json',before)
 audit={
  'A4_NATIVE_MODE_SUPPORTED':'NO',
  'CURRENT_GATE':'A4_NATIVE_CURVE_ONLY_MODE_UNSUPPORTED_BLOCKED',
  'config_interface_search':'no use_surface/surface_enabled/disable_surface/curve_only native option found',
  'dataset_collator_trace':'SpatialLMPlugin._get_mm_inputs in cad_separate_edge_tokens mode calls _load_cad_separate_edge and appends both point_clouds_data and edge_clouds_data',
  'model_forward_trace':'SpatialLMLlama forward enters geometry only when point_clouds is not None; each item calls forward_geometry(point_cloud, edge_cloud, ...)',
  'surface_trace':'official curve-token forward_geometry always calls forward_point_cloud(surface_points, projector=point_proj) before projecting curves',
  'curve_without_surface_result':'edge_clouds alone are ignored because the geometry branch is guarded by point_clouds is not None',
  'native_empty_surface_result':'no official empty-surface contract located',
  'dummy_or_zero_surface_used':'NO','monkey_patch_used':'NO','main_method_source_modified':'NO',
  'A4_TRAINING_STARTED':'NO','reason':'A4 would require forbidden behavior changes to Dataset/Collator/model/curve injector'
 }
 dump(OUT/'audits/A4_NATIVE_RUNTIME_INTERFACE_AUDIT.json',audit)
 cfg={'EXPERIMENT':'A4_ALL_CURVES_ONLY','ABLATION_ROLE':'MODALITY_SUFFICIENCY','requested_surface_modality':'ABSENT','requested_curve_modality':'ALL_RETAINED_CURVES','BASE_HASH':'df46dc4c4c015cf607e0f76ab6f74694d965045f987029609c96e0a488d2292aa','PROJECTOR':'256->256->GELU->2048','PROJECTOR_PARAM_N':592128,'C2_SHA256':'553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9','TRAIN_N':7998,'VAL_N':1000,'TEST_N':1000,'NUM_EPOCHS':20,'TRAINING_ENABLED':False,'blocked_before_config_launch':True}
 dump(OUT/'configs/A4_CONFIG_FREEZE.json',cfg)
 gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True).splitlines()
 resource={'A4_GPU_CANDIDATE':1,'A4_GPU_INDEPENDENT':'YES','A4_TRAINING_STARTED':'NO','reason':'native runtime gate failed before resource allocation','gpu_snapshot':gpu,'ram_available_bytes':int(os.sysconf('SC_AVPHYS_PAGES')*os.sysconf('SC_PAGE_SIZE')),'disk_free_bytes':os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize}
 dump(OUT/'audits/A4_RESOURCE_ISOLATION_AUDIT.json',resource)
 after=inventory();dump(OUT/'audits/MAIN_METHOD_SOURCE_INVENTORY_AFTER.json',after)
 changed=[a['path'] for a,b in zip(before,after) if a!=b]
 final={'CURRENT_GATE':'A4_NATIVE_CURVE_ONLY_MODE_UNSUPPORTED_BLOCKED','A4_NATIVE_MODE_SUPPORTED':'NO','A4_TRAINING_STARTED':'NO','A4_TRAINING_COMPLETE':'NO','NEXT_STEP':'future isolated implementation only if separately authorized','MAIN_METHOD_CODE_CHANGED':'NO' if not changed else 'YES','SOURCE_CHANGED_N':len(changed),'SOURCE_CHANGED_PATHS':changed,'EXACT9998_CHANGED':'NO','CURVE_TOKEN_CACHE_CHANGED':'NO','C2_CHANGED':'NO','A0_CHANGED':'NO','A1_CHANGED':'NO','A2_CHANGED':'NO','A3_CHANGED':'NO','TEST_FORWARD':'NO','TEST_DECODE':'NO','TEST_METRIC':'NO','TEST_GEOMETRY':'NO'}
 dump(OUT/'reports/FINAL_REPORT.json',final);dump(OUT/'reports/A4_TRAINING_STATUS.json',final)
 (OUT/'reports/FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in final.items())+'\n')
 print(json.dumps(final,indent=2))
if __name__=='__main__':main()
