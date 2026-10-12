from pathlib import Path
import json,hashlib,re,gzip,base64
from PIL import Image
r=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922');root=r/'assemblies';rows=json.loads((root/'review/manifest.json').read_text());assert len(rows)==77 and sum(x['parts'] for x in rows)==793
for row in rows:
    case=row['case_id'];d=root/case;expected_solids=0
    for part,h in row['part_step_sha256'].items():
        p=r/'cases'/case/part;assert hashlib.sha256((p/'model.step').read_bytes()).hexdigest()==h
        expected_solids+=json.loads((p/'report.json').read_text())['cad_solids']
    assert row['assembly_solids']==expected_solids,(case,row['assembly_solids'],expected_solids)
    for name,size in [('assembly.png',(2000,1720)),('cover.png',(1000,850)),('source_vs_assembly.png',(2000,870))]:
        with Image.open(d/name) as im:assert im.size==size;im.verify()
    text=(d/'interactive.html').read_text();manifest=json.loads(re.search(r'const manifest=(.*?);const packed=',text).group(1));payload=re.search(r"const packed='([^']*)';",text).group(1);data=gzip.decompress(base64.b64decode(payload));assert len(manifest['parts'])==row['parts']
    for p in manifest['parts']:
        for key in ('positions','normals','indices','edges'):
            desc=p[key];assert desc['offset']%4==0 and desc['offset']+desc['count']*4<=len(data)
        assert p['positions']['count']==p['normals']['count'] and p['indices']['count']%3==0
assert not (root/'tank').exists()
result=dict(cases=77,parts=793,assembly_step_solids_preserved=True,part_step_hashes_unchanged=True,all_images_verified=True,all_interactive_payloads_verified=True,tank_skipped=True,accepted_parts=sum(x['accepted'] for x in rows),needs_refinement_parts=sum(x['needs_refinement'] for x in rows))
(root/'assembly_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
