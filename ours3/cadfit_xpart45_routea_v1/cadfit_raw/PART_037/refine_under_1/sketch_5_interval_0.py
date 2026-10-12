import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.24529, 0.12058, 0.14855), normal=(-0.00077, 0.03706, -0.99931), xDir=(0.0, -0.99931, -0.03706))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23639, -0.92505)
loop_1 = loop_1.lineTo(0.23614, -0.91141)
loop_1 = loop_1.lineTo(0.23443, -0.89777)
loop_1 = loop_1.threePointArc((0.23153, -0.89045), (0.229, -0.88413))
loop_1 = loop_1.lineTo(0.21475, -0.89544)
loop_1 = loop_1.lineTo(0.21133, -0.91141)
loop_1 = loop_1.lineTo(0.2112, -0.92505)
loop_1 = loop_1.lineTo(0.21362, -0.9387)
loop_1 = loop_1.lineTo(0.22343, -0.95234)
loop_1 = loop_1.lineTo(0.23531, -0.9387)
loop_1 = loop_1.lineTo(0.23632, -0.92591)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_5_interval_0.stl')