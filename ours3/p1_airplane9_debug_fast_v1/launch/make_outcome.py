from pathlib import Path
import json
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1');parts=[f'PART_{i:03d}' for i in range(9)]
def r(p):return json.loads(p.read_text())
rows=[r(E/f'evaluations/checkpoint-80/{p}/result.json') for p in parts]
summary={'step':80,'checkpoint':str(E/'runs/quick/checkpoint-80'),'exact_n':sum(x['SEQUENCE_EXACT_MATCH'] for x in rows),'gate_n':sum(x['PART_GATE_PASS'] for x in rows),'cad_step_n':sum(x['CAD_EXECUTION_PASS'] and x['STEP_READBACK_PASS'] for x in rows),'tf_errors':sum(x['TOKEN_ERRORS'] for x in rows)}
(E/'evaluations/checkpoint-80/summary.json').write_text(json.dumps(summary,indent=2))
traj=r(E/'trajectory.json');
for x in traj:
 if x['step']==80:x['free_exact_n']=summary['exact_n']
(E/'trajectory.json').write_text(json.dumps(traj,indent=2));best={'step':60,'checkpoint':str(E/'runs/quick/checkpoint-60'),'exact_n':9,'gate_n':9,'cad_step_n':9,'tf_errors':0}
(E/'best_checkpoint.json').write_text(json.dumps(best,indent=2));(E/'outcome.json').write_text(json.dumps({'P1_A3_GATE':'PASS','FIRST_9_OF_9_TF_ZERO_CHECKPOINT':str(E/'runs/quick/checkpoint-60'),'FIRST_9_OF_9_EXACT_CHECKPOINT':str(E/'runs/quick/checkpoint-60'),'EXACT_MEMORIZATION_STABLE':summary['gate_n']==9,'best':best,'training_returncode':0},indent=2))
