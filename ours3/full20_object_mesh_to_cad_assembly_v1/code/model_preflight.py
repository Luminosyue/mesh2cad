import os,json,sys,shutil
from pathlib import Path
import numpy as np
import torch,transformers,flash_attn
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/full20_object_mesh_to_cad_assembly_v1'
C=R/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1/frozen_tf5_success_v1'
from transformers import AutoTokenizer
t=AutoTokenizer.from_pretrained(C,use_fast=False)
rows=[]
for p in sorted((O/'objects').glob('*/cad_parts/*/result.json')):
 r=json.loads(p.read_text()); ir=p.parent/'compact_ir_v3.v3'
 rows.append(dict(object=r['OBJECT_ID'],part=r['PART_ID'],passed=r['PASS'],reason=r['FAILURE_REASON'],tokens=len(t.encode(ir.read_text(),add_special_tokens=False)) if ir.exists() else None))
E=O/'model_v1';(E/'reports').mkdir(parents=True,exist_ok=True)
(E/'reports/LABEL_CONTEXT_AUDIT.json').write_text(json.dumps(rows,indent=2))
print('RUNTIME',sys.executable,torch.__version__,transformers.__version__)
for obj in sorted(set(r['object'] for r in rows)):
 rr=[r for r in rows if r['object']==obj];print(obj,len(rr),sum(r['passed'] for r in rr),max([r['tokens'] or 0 for r in rr]),'target tokens max')
a=np.load(R/'ours3/p3_xpart_20case_compact_ir_v1/dataset/case_018_surface_points.npy'); print('OLD_POINTS',a.shape,a.min(0),a.max(0))
print('CHECKPOINT_GB',sum(p.stat().st_size for p in C.glob('*.safetensors'))/1e9)
print('TRAIN_ENV',[(k,v) for k,v in os.environ.items() if k in ['CONDA_PREFIX','LD_LIBRARY_PATH','DISABLE_VERSION_CHECK']])
