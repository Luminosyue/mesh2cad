from pathlib import Path
import zipfile,json
root=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/cadrille_cadrecode_parts21_20260926_v2')
out=root/'deliverables'
with zipfile.ZipFile(out/'case_previews.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in (out/'previews').glob('*.png'):z.write(p,p.relative_to(out))
print('preview archive', (out/'case_previews.zip').stat().st_size)
print('pipeline_done',(root/'PIPELINE_DONE.json').exists())
print('source_zip_bytes',(out/'source_parts_and_previews.zip').stat().st_size)
