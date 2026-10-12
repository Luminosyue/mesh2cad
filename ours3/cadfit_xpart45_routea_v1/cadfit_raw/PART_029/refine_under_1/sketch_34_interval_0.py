import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.07579, -0.18022, 0.12758), normal=(-0.0362, 0.88964, -0.45522), xDir=(0.99917, 0.04065, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.05287, -0.03432)
loop_1 = loop_1.lineTo(1.06337, -0.03807)
loop_1 = loop_1.lineTo(1.07872, -0.05808)
loop_1 = loop_1.threePointArc((1.07987, -0.06708), (1.08091, -0.07534))
loop_1 = loop_1.threePointArc((1.07653, -0.07054), (1.07388, -0.06238))
loop_1 = loop_1.threePointArc((1.04082, -0.06839), (1.01009, -0.07399))
loop_1 = loop_1.lineTo(1.01081, -0.05919)
loop_1 = loop_1.lineTo(1.01956, -0.04287)
loop_1 = loop_1.lineTo(1.03391, -0.03361)
loop_1 = loop_1.threePointArc((1.04121, -0.03331), (1.04717, -0.033))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_34_interval_0.stl')