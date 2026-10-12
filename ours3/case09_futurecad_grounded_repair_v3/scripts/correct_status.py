import json
from pathlib import Path
root=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/case09_futurecad_grounded_repair_v3')
for rel in ['metrics/summary.json','07_final_qa/final_qa.json']:
 p=root/rel;d=json.loads(p.read_text());met=d['V3_SHARP_EDGE_RECALL']>=.97;d['SHARP_EDGE_TARGET']=.97;d['SHARP_EDGE_TARGET_MET']=met
 if not met:
  d['CURRENT_GATE']='CASE09_FUTURECAD_GROUNDED_REPAIR_V3_PARTIAL_PASS';d['BLOCKERS']=['SHARP_EDGE_RECALL_TARGET_0.97_NOT_REACHED']
 p.write_text(json.dumps(d,indent=2)+'\n')
report=root/'report.md';text=report.read_text().replace('Gate: `CASE09_FUTURECAD_GROUNDED_REPAIR_V3_PASS`','Gate: `CASE09_FUTURECAD_GROUNDED_REPAIR_V3_PARTIAL_PASS`');text+='\n## Unmet target\n\n- Sharp-edge recall improved to 0.9560439560 but did not reach the 0.97 target. Additional tested edge-dense candidates reached 0.9735669736 only by failing the per-part Q1/Q2 hard gate, so they were correctly rejected.\n';report.write_text(text)
