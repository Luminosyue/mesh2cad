import json,csv
from pathlib import Path
p=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p3_xpart_v3_optimizer_memory_demo5_v1')
rows=[]
for step in [40,80,160]:
    data=json.loads((p/'eval'/f'TF_SCAN_{step:03d}.json').read_text())
    rows.append({'checkpoint':step,'total_errors':sum(x['tf_error_n'] for x in data),'zero_error_case_n':sum(x['tf_error_n']==0 for x in data),'case_n':len(data)})
with (p/'eval/TF_ERROR_TRAJECTORY.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
