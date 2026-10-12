import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.17695, 0.0533, 0.17558), normal=(0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.25098, 0.82305)
loop_1 = loop_1.lineTo(0.25098, -1.17695)
loop_1 = loop_1.lineTo(-0.14437, -1.17695)
loop_1 = loop_1.lineTo(-0.14437, 0.82305)
loop_1 = loop_1.lineTo(0.22264, 0.82305)
loop_1 = loop_1.lineTo(0.25098, 0.82305)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.0533, -0.82811)
loop_2 = loop_2.circle(0.04593)
loop_3 = sketch_1.moveTo(0.0533, 0.47421)
loop_3 = loop_3.circle(0.04593)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3)
solid_1 = sketch_1.extrude(0.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0079_00797643/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0079_00797643/sketch_3_interval_0.stl')