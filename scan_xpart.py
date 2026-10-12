from pathlib import Path
import trimesh, json
root=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')
rows=[]
for p in sorted(root.rglob('*')):
    if not p.is_file() or p.suffix.lower() not in ('.obj','.stl') or p.parent.name not in ('p3_parts','xpart_parts'):
        continue
    try:
        m=trimesh.load(p,force='mesh',process=False); m.merge_vertices(); m.remove_unreferenced_vertices()
        rows.append({'path':str(p.relative_to(root)),'v':len(m.vertices),'f':len(m.faces),'watertight':bool(m.is_watertight),'volume':bool(m.is_volume),'extents':m.extents.tolist(),'components':len(m.split(only_watertight=False))})
    except Exception as e: rows.append({'path':str(p.relative_to(root)),'v':0,'f':0,'watertight':False,'volume':False,'extents':[],'components':0,'error':repr(e)})
print(json.dumps({'n':len(rows),'watertight':sum(x['watertight'] for x in rows),'volume':sum(x['volume'] for x in rows),'p3':sum('/p3_parts/' in x['path'] for x in rows),'xpart':sum('/xpart_parts/' in x['path'] for x in rows)},indent=2))
for x in rows[:160]: print(x)
