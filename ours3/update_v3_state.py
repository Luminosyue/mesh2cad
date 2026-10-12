import json
from pathlib import Path
p=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p3_xpart_20case_compact_ir_v3/reports/experiment_state.json')
d=json.loads(p.read_text())
d['v3_memory_gate']='FAIL_OPTIMIZER_STATE_OOM'
d['memory_probe']={'status':'INCOMPLETE_UPDATE_1','input_length':12065,'attention_impl':'sdpa','use_cache':False,'gradient_checkpointing':True,'optimizer_state_lazy_allocation':'OOM','concurrent_gpu_occupancy':True}
d['demo5_overfit']='NOT_STARTED_MEMORY_GATE'
d['twenty_case_overfit']='NOT_STARTED_MEMORY_GATE'
p.write_text(json.dumps(d,indent=2))
