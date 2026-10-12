import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0141, 0.1, -0.04406), normal=(0.0, -1.0, -0.0), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.9859, 0.40594)
loop_1 = loop_1.lineTo(-1.0141, 0.40594)
loop_1 = loop_1.lineTo(-1.0141, -0.09406)
loop_1 = loop_1.lineTo(-0.6141, -0.49406)
loop_1 = loop_1.lineTo(-0.0141, -0.49406)
loop_1 = loop_1.lineTo(-0.0141, -0.09406)
loop_1 = loop_1.lineTo(0.3859, -0.09406)
loop_1 = loop_1.lineTo(0.3859, -0.49406)
loop_1 = loop_1.lineTo(0.7859, -0.49406)
loop_1 = loop_1.lineTo(0.9859, -0.29406)
loop_1 = loop_1.lineTo(0.9859, 0.37506)
loop_1 = loop_1.lineTo(0.9859, 0.40594)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0027_00271439/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0027_00271439/sketch_0_interval_0.stl')