import json
from pathlib import Path
p=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p3_xpart_v3_optimizer_memory_demo5_v1/reports/experiment_state.json')
d=json.loads(p.read_text())
d.update({'experiment':'DEMO5_FULL_PIPELINE_FINALIZATION_V1','step160_model_still_alive':'NO_RECONSTRUCTED_FROM_CHECKPOINT40','frozen_checkpoint':'frozen_tf5_success_v1','frozen_checkpoint_tf_exact':'5/5','demo5_tf_exact':'5/5','demo5_free_exact':'5/5','demo5_natural_eos':'5/5','demo5_parser_compiler':'5/5','demo5_cad_brep':'5/5','demo5_cad_step':'5/5','demo5_step_readback':'5/5','demo5_geometry_exact':'5/5','new5_model_exact_pass':True,'new5_full_pipeline_pass':True,'new_case_teaser_ready':True,'twenty_case_joint':'NOT_STARTED','next_gate':'P3_XPART_20CASE_V3_JOINT_OVERFIT'})
p.write_text(json.dumps(d,indent=2))
