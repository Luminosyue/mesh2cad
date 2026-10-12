import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00305, 0.10457, -0.30355), normal=(-0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.10457, 1.00305)
loop_1 = loop_1.lineTo(-1.10457, -0.99695)
loop_1 = loop_1.lineTo(0.89543, -0.99695)
loop_1 = loop_1.lineTo(0.89543, 1.00305)
loop_1 = loop_1.lineTo(-1.06464, 1.00305)
loop_1 = loop_1.lineTo(-1.10457, 1.00305)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-1.07231, 0.97079)
loop_2 = loop_2.lineTo(0.86317, 0.97079)
loop_2 = loop_2.lineTo(0.86317, -0.96469)
loop_2 = loop_2.lineTo(-1.07231, -0.96469)
loop_2 = loop_2.lineTo(-1.07231, 0.93132)
loop_2 = loop_2.lineTo(-1.07231, 0.97079)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.61)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0093_00934604/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0093_00934604/sketch_1_interval_0.stl')