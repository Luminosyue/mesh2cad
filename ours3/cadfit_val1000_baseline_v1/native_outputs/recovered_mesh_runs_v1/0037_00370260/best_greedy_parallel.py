import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00375, -0.01295, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.56958, 0.23135)
loop_1 = loop_1.lineTo(-0.56958, -0.23886)
loop_1 = loop_1.lineTo(-0.29497, -0.51346)
loop_1 = loop_1.lineTo(0.32087, -0.51346)
loop_1 = loop_1.lineTo(0.59548, -0.23886)
loop_1 = loop_1.lineTo(0.59548, 0.23135)
loop_1 = loop_1.lineTo(0.32087, 0.50595)
loop_1 = loop_1.lineTo(-0.29497, 0.50595)
loop_1 = loop_1.lineTo(-0.56786, 0.23307)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0037_00370260/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0037_00370260/sketch_2_interval_0.stl')