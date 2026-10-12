import json
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad')
O=R/'ours3/m2_fusion360_canonicalization_contract_diagnostic_v1'
O.mkdir(parents=True,exist_ok=True)
rows=[json.loads(x) for x in (R/'ours3/fusion360_dora_free_overlap602_recovery_v1/OVERLAP602_EXECUTION_MERGED.jsonl').read_text().splitlines() if x]
common=[x['cad_id'] for x in rows if x['historical']['terminal_status']=='PASS' and x['p1_sampled']['terminal_status']=='PASS' and x['historical']['step_reload'] and x['p1_sampled']['step_reload']]
if len(common)!=592: raise RuntimeError(len(common))
(O/'COMMON_VALID_SUBSET.json').write_text(json.dumps({'COMMON_EXEC_VALID_N':592,'cad_ids':common},indent=2)+'\n')
(O/'HISTORICAL_TRANSFORM_SEMANTICS_AUDIT.json').write_text(json.dumps({'forward_formula':'p_canonical=scale*p_source+translation','inverse_formula':'p_source=(p_canonical-translation)/scale','scale':'6/diag','translation':'-scale*bbox_min'},indent=2)+'\n')
(O/'FUSION360_COORDINATE_FRAME_GRAPH.json').write_text(json.dumps({'FRAME_A':'raw JSON/source program','FRAME_B':'raw OBJ/sampled mesh','FRAME_C':'raw STEP','FRAME_D':'historical canonical M2','known_edge':'B_to_D historical frozen transform','unknown_edges':['A_to_B','A_to_C','C_to_D']},indent=2)+'\n')
(O/'SOURCE_GEOMETRY_AUTHORITY_DECISION_REQUIRED.json').write_text(json.dumps({'status':'DECISION_REQUIRED','candidates':['program_OBJ','raw_STEP'],'reason':'source-frame fidelity requires formal raw JSON/OBJ/STEP relation'},indent=2)+'\n')
(O/'FINAL_REPORT.json').write_text(json.dumps({'CURRENT_GATE':'M2_FUSION360_SOURCE_ASSET_DOMAIN_MISMATCH_CONFIRMED','CANONICALIZATION_PROTOCOL_STATUS':'UNRESOLVED','COMMON_EXEC_VALID_N':592,'FULL8625_ALLOWED':'NO','TRAINING_RUN':'NO','DECODE_RUN':'NO','NEXT_STEP':'M2_FUSION360_SOURCE_GEOMETRY_AUTHORITY_DECISION_V1'},indent=2)+'\n')
