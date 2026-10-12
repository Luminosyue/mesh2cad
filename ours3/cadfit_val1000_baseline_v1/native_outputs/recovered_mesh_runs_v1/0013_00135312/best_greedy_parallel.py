import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.21695, -0.77, 0.21754), normal=(-0.0, 1.0, 0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.92283, 1.21754)
loop_1 = loop_1.lineTo(-0.92283, -0.78246)
loop_1 = loop_1.lineTo(0.48894, -0.78246)
loop_1 = loop_1.lineTo(0.48894, 1.21754)
loop_1 = loop_1.lineTo(-0.8874, 1.21754)
loop_1 = loop_1.lineTo(-0.92283, 1.21754)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.54)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0013_00135312/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0013_00135312/sketch_3_interval_0.stl')