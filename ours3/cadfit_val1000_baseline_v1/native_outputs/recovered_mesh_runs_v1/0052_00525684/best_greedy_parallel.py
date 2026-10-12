import cadquery as cq
import math

plane_1 = cq.Plane(origin=(1.0, 0.00304, -0.0009), normal=(-1.0, -0.0, -0.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.09193, 0.04354)
loop_1 = loop_1.lineTo(-0.09193, -0.04535)
loop_1 = loop_1.lineTo(0.01474, -0.04535)
loop_1 = loop_1.lineTo(0.04418, -0.04535)
loop_1 = loop_1.lineTo(0.08585, -0.04535)
loop_1 = loop_1.lineTo(0.08585, 0.04354)
loop_1 = loop_1.lineTo(-0.08918, 0.04354)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0052_00525684/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0052_00525684/sketch_0_interval_0.stl')