from pathlib import Path
import shutil, json, os
root=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')
for p in [Path('/AGENTS.md'),*[x/'AGENTS.md' for x in root.parents],root/'AGENTS.md',*root.rglob('AGENTS.md')]:
    if p.is_file(): print(str(p),p.read_text())
print('Xvfb',shutil.which('Xvfb'),'xvfb-run',shutil.which('xvfb-run'))
print('DISPLAY',os.environ.get('DISPLAY'))
files=[p for p in root.glob('*/xpart_parts/PART_*/complete_part_*.obj') if p.relative_to(root).parts[0]!='tank']
print('PARTS',len(files),'CASES',len(set(p.relative_to(root).parts[0] for p in files)))
print('FONT',list(Path('/usr/share/fonts').rglob('*CJK*'))[:5])
