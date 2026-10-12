import json
from pathlib import Path
p=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p3_xpart_v3_optimizer_memory_demo5_v1/reports/experiment_state.json')
d=json.loads(p.read_text()) if p.exists() else {}
d.update({'experiment':'P3_XPART_V3_OPTIMIZER_MEMORY_AND_DEMO5_V1','v3_memory_gate':'PASS','optimizer_memory_gate':'PASS','selected_optimizer':'AdamW','selected_state_placement':'GPU','trainable_mode':'FULL_PARAMETER','context':16384,'micro_batch':1,'demo5_tf_zero_checkpoint':160,'demo5_tf_exact':'5/5','demo5_free_exact':'1/5_COMPLETED_TANK','demo5_cad_step':'1/5_COMPLETED_TANK','tank_case':'case_014_PART_029','twenty_case_joint':'NOT_STARTED','next_gate':'NEW5_FAST_REFINEMENT'})
p.write_text(json.dumps(d,indent=2))
