"""Usage: python regenerate_case.py ../cadrille/android_figure_orange
Requires CadQuery. Edit the per-part cadquery.py files, then rebuild the assembly.
"""
import json,runpy,sys
from pathlib import Path
import cadquery as cq

folder=Path(sys.argv[1]).resolve()
assembly=cq.Assembly(name=folder.name)
for part in sorted((folder/'parts').iterdir()):
    if not (part/'cadquery.py').exists():continue
    meta=json.loads((part/'transform.json').read_text())
    ns=runpy.run_path(str(part/'cadquery.py'))
    obj=next(ns[k] for k in ['r','result','shape'] if k in ns)
    if isinstance(obj,cq.Workplane):
        vals=obj.vals();shape=cq.Compound.makeCompound(vals) if len(vals)>1 else vals[0]
    else:shape=obj
    shape=shape.scale(meta['world_scale']).translate(tuple(meta['center']))
    assert shape.isValid(),part
    cq.exporters.export(shape,str(part/'edited_world.step'))
    assembly.add(shape,name=part.name)
assembly.save(str(folder/'edited_assembled.step'))
print(folder/'edited_assembled.step')
