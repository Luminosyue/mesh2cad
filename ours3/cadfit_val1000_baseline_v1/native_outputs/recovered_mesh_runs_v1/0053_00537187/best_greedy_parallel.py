import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.23, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.94148, 1.0)
loop_1 = loop_1.lineTo(-0.93755, -0.01626)
loop_1 = loop_1.lineTo(0.94148, -0.99335)
loop_1 = loop_1.lineTo(0.93714, 0.59784)
loop_1 = loop_1.lineTo(-0.93931, 0.99954)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.46)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0053_00537187/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0053_00537187/sketch_2_interval_0.stl')