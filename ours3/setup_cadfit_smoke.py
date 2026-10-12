from pathlib import Path
import csv
B=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
C=B/'cadfit_val1000_baseline_v1'; S=C/'smoke10_input'; S.mkdir(exist_ok=True)
rows=list(csv.DictReader((C/'provenance/CADFIT_VAL1000_MANIFEST.csv').open()))[:10]
for r in rows:
    src=C/'input_recovered_v2'/(r['case_id'].replace('deepcad__','')+'.stl')
    dst=S/(r['case_id']+'.stl')
    if not dst.exists(): dst.symlink_to(src)
(C/'smoke10_case_ids.txt').write_text('\n'.join(r['case_id'] for r in rows)+'\n')
print('\n'.join(r['case_id'] for r in rows))
