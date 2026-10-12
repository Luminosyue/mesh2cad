import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.66667, 0.83333)
loop_1 = loop_1.lineTo(0.66467, 0.16667)
loop_1 = loop_1.lineTo(0.0, 0.16467)
loop_1 = loop_1.lineTo(-0.004, -0.83333)
loop_1 = loop_1.lineTo(-0.66667, -0.83133)
loop_1 = loop_1.lineTo(-0.66267, 0.83333)
loop_1 = loop_1.lineTo(0.66467, 0.83333)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0035_00359882/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0035_00359882/sketch_3_interval_0.stl')