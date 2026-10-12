import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0042, -0.00034), normal=(1.0, -0.0, 0.0), xDir=(-0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0042, -0.00034)
loop_1 = loop_1.circle(0.08677)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__22025_b77024b9_0006/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__22025_b77024b9_0006/sketch_0_interval_0.stl')