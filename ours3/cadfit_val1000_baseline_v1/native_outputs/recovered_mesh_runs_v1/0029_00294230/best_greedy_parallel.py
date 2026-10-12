import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.06032, -1.0, -0.00467), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.23032, 0.15533)
loop_1 = loop_1.lineTo(-0.23032, 0.11533)
loop_1 = loop_1.lineTo(0.04968, 0.11533)
loop_1 = loop_1.lineTo(0.04968, -0.12467)
loop_1 = loop_1.lineTo(-0.23032, -0.12504)
loop_1 = loop_1.lineTo(-0.23032, -0.16467)
loop_1 = loop_1.lineTo(0.10968, -0.16467)
loop_1 = loop_1.lineTo(0.10968, 0.15533)
loop_1 = loop_1.lineTo(-0.22819, 0.15533)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0029_00294230/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0029_00294230/sketch_8_interval_0.stl')