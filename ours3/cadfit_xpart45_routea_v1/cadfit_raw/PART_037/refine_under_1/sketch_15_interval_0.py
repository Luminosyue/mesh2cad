import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00747, -0.00135, 0.15606), normal=(-0.00071, 0.0199, -0.9998), xDir=(0.0, -0.9998, -0.0199))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10374, -0.72051)
loop_1 = loop_1.lineTo(0.11602, -0.72214)
loop_1 = loop_1.lineTo(0.12489, -0.65869)
loop_1 = loop_1.lineTo(0.17785, -0.64505)
loop_1 = loop_1.lineTo(0.12078, -0.65047)
loop_1 = loop_1.lineTo(0.11801, -0.6374)
loop_1 = loop_1.lineTo(0.17562, -0.60412)
loop_1 = loop_1.lineTo(0.10748, -0.6212)
loop_1 = loop_1.lineTo(0.0953, -0.61934)
loop_1 = loop_1.lineTo(-0.17566, -0.45395)
loop_1 = loop_1.lineTo(0.08126, -0.63109)
loop_1 = loop_1.lineTo(0.07568, -0.64505)
loop_1 = loop_1.lineTo(0.07525, -0.65869)
loop_1 = loop_1.lineTo(0.07618, -0.66904)
loop_1 = loop_1.lineTo(0.08046, -0.68306)
loop_1 = loop_1.lineTo(0.10374, -0.72051)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_15_interval_0.stl')