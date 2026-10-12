import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.08453, -0.3113, -0.80034), normal=(-0.24649, 0.96905, 0.01387), xDir=(0.96914, 0.24652, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.22064, 0.00437)
loop_1 = loop_1.lineTo(0.28456, 0.00437)
loop_1 = loop_1.lineTo(0.2733, -0.01096)
loop_1 = loop_1.lineTo(0.23994, -0.02696)
loop_1 = loop_1.lineTo(0.22189, -0.00314)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.62)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_1_interval_0.stl')