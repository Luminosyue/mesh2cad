import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.66667, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.5)
loop_1 = loop_1.lineTo(-0.99621, -0.5)
loop_1 = loop_1.lineTo(-0.33333, -0.4981)
loop_1 = loop_1.lineTo(-0.32967, 0.14371)
loop_1 = loop_1.lineTo(0.98673, 0.5)
loop_1 = loop_1.lineTo(-0.9981, 0.5)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0004_00044623/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0004_00044623/sketch_0_interval_0.stl')