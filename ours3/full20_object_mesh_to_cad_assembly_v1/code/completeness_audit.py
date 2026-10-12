import json,csv
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad');S=R/'p3_xpart_open_cases';O=R/'ours3/full20_object_mesh_to_cad_assembly_v1'
rows=[]
for c in sorted(S.iterdir()):
 if not (c/'meta.json').exists():continue
 meta=json.loads((c/'meta.json').read_text());pm=c/'p3_parts/part_metadata.json';partmeta=json.loads(pm.read_text()) if pm.exists() else {};xp=c/'xpart_manifest.json';xm=json.loads(xp.read_text()) if xp.exists() else {}
 p3=sorted((c/'p3_parts').glob('part_*.obj'));xpfiles=sorted(p for p in (c/'xpart_parts').rglob('*') if p.suffix.lower() in ['.obj','.stl','.ply']);pids={p.stem.upper() for p in p3};xids={p.stem.upper() if p.parent.name=='xpart_parts' else p.parent.name.upper() for p in xpfiles}
 counts=[len(p3),int(meta.get('n_p3_parts',0)),int(partmeta.get('num_parts',0)),int(xm.get('XPART_ATTEMPTED_PARTS',0))];expected=max(counts);gate=expected>=2 and len(xids)==expected and pids==xids
 rows.append(dict(OBJECT_ID=c.name,EXPECTED_PART_N=expected,P3_FILE_N=len(p3),XPART_FILE_N=len(xids),COMPLETE=gate,MISSING_IDS=','.join(sorted(pids-xids)),COUNT_EVIDENCE=str(counts)))
with (O/'selection/FULL_PART_SET_CORRECTION_AUDIT.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print('COMPLETE CANDIDATES',sum(r['COMPLETE'] for r in rows));print('\n'.join(f"{r['OBJECT_ID']} | {r['EXPECTED_PART_N']}" for r in rows if r['COMPLETE']))
old=json.loads((O/'manifests/FULL20_OBJECT_MANIFEST.json').read_text());names={x['OBJECT_ID'] for x in old};print('CURRENT_SELECTION');print('\n'.join(f"{r['OBJECT_ID']} | expected {r['EXPECTED_PART_N']} | have {r['XPART_FILE_N']} | {r['COMPLETE']}" for r in rows if r['OBJECT_ID'] in names))
