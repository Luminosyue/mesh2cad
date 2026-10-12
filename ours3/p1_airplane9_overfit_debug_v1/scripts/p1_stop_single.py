from pathlib import Path
import os,signal,json
root=Path('/data/home/cuiyuehan/project/mesh2cad');single=root/'ours3/p1_single_airplane_part_overfit_v1';debug=root/'ours3/p1_airplane9_overfit_debug_v1'
gate=json.loads((debug/'single_checks/checkpoint-500/single_case_decode_diagnosis.json').read_text());assert gate['SINGLE_PART_EXACT_OVERFIT']=='PASS'
state=json.loads((single/'status.json').read_text());pid=state['pid']
cmd=Path(f'/proc/{pid}/cmdline').read_bytes().decode();assert str(single/'launch/cq54_train.py') in cmd
os.kill(pid,signal.SIGTERM);os.kill(pid,signal.SIGCONT)
state.update(state='STOPPED_AFTER_GATE_PASS',reason='Stage 9 paused further steps; saved checkpoint-500 already meets every exact-overfit gate. No need to extend to 1000/2000.',passing_checkpoint=str(single/'runs/quick/checkpoint-500'),saved_checkpoints=[100,200,500],last_observed_progress=json.loads((debug/'single_training_pause.json').read_text())['last_progress'])
(single/'status.json').write_text(json.dumps(state,indent=2));print(json.dumps(state))
