import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0056, -0.00086), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01646, 0.04326)
loop_1 = loop_1.lineTo(0.00043, 0.0399)
loop_1 = loop_1.lineTo(0.01474, 0.03034)
loop_1 = loop_1.lineTo(0.0243, 0.01602)
loop_1 = loop_1.lineTo(0.02766, -0.00086)
loop_1 = loop_1.lineTo(0.0243, -0.01774)
loop_1 = loop_1.lineTo(0.01474, -0.03206)
loop_1 = loop_1.lineTo(0.00043, -0.04162)
loop_1 = loop_1.lineTo(-0.01646, -0.04498)
loop_1 = loop_1.lineTo(-0.01646, 0.04215)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0052_00526102/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0052_00526102/sketch_0_interval_0.stl')