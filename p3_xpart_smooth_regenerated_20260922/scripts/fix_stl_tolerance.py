from pathlib import Path
import sys
before='tolerance=0.025/PARAMETERS["construction_scale"]'
after='tolerance=0.025'
if '--local' in sys.argv:
    root=Path(__file__).parent;paths=[root/'regenerate_smooth.py',root/'regularize_part.py']
else:
    root=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
    paths=[root/'scripts/regenerate_smooth.py',root/'scripts/regularize_part.py']
    paths += [p for folder in ('cases','refinements','regularized_trials') for p in (root/folder).glob('*/*/cad.py')]
changed=0
for p in paths:
    if not p.exists():continue
    code=p.read_text()
    if before in code:p.write_text(code.replace(before,after));changed+=1
print('Updated relative STL tolerance in',changed,'scripts')
