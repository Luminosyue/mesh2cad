import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.32571, -0.02516, -0.23483), normal=(-0.03591, 0.70778, 0.70552), xDir=(0.99872, 0.05067, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.84172, -0.02529)
loop_1 = loop_1.lineTo(0.85625, -0.02201)
loop_1 = loop_1.lineTo(0.89458, -0.03081)
loop_1 = loop_1.lineTo(0.98045, -0.03133)
loop_1 = loop_1.lineTo(0.91429, -0.03953)
loop_1 = loop_1.lineTo(0.8956, -0.03698)
loop_1 = loop_1.lineTo(0.87739, -0.03401)
loop_1 = loop_1.lineTo(0.85965, -0.0307)
loop_1 = loop_1.lineTo(0.83599, -0.04415)
loop_1 = loop_1.lineTo(0.83013, -0.06556)
loop_1 = loop_1.threePointArc((0.83027, -0.05188), (0.83035, -0.04479))
loop_1 = loop_1.lineTo(0.84171, -0.0253)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_46_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_46_interval_0.stl')