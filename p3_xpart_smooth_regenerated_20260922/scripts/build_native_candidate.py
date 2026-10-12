"""Run one OCC operation in its own process, so a bad loft cannot stall a part."""
import sys,json
from pathlib import Path
runtime_source=Path(__file__).with_name('smooth_runtime.py').read_text()
runtime_ns={};exec(compile(runtime_source,'smooth_runtime.py','exec'),runtime_ns)
build_normalized=runtime_ns['build_normalized']
import numpy as np,trimesh
from regenerate_smooth import tess,evaluate
spec=json.load(open(sys.argv[1]))
shape=build_normalized(spec)
if not shape.isValid() or not shape.Solids():raise ValueError('Native feature is not a valid solid')
if len(shape.Faces())>250:raise ValueError('Excessive CAD face complexity')
data=np.load(sys.argv[3]);source=trimesh.Trimesh(data['vertices'],data['faces'],process=False)
cm=tess(shape)
if len(cm.faces)>500000:raise ValueError('Unstable tessellation complexity')
quality=evaluate(source,cm,2048)
shape.exportBrep(sys.argv[2])
with open(sys.argv[4],'w') as f:json.dump(quality,f)
Path(sys.argv[2]).with_name('candidate_runtime.txt').write_text(runtime_source)
