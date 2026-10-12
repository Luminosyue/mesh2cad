import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.44619, 0.07598, 0.01518), normal=(-0.24856, -0.96862, -0.00047), xDir=(-0.96862, 0.24856, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.19229, 0.4995)
loop_1 = loop_1.threePointArc((0.18259, 0.5088), (0.17249, 0.51848))
loop_1 = loop_1.lineTo(0.15314, 0.53526)
loop_1 = loop_1.lineTo(0.12519, 0.55665)
loop_1 = loop_1.lineTo(0.1072, 0.56975)
loop_1 = loop_1.threePointArc((0.06538, 0.59716), (0.02677, 0.62109))
loop_1 = loop_1.threePointArc((0.01355, 0.62734), (0.00282, 0.63237))
loop_1 = loop_1.lineTo(0.01279, 0.61945)
loop_1 = loop_1.lineTo(0.02938, 0.60485)
loop_1 = loop_1.threePointArc((0.03819, 0.59832), (0.04471, 0.59354))
loop_1 = loop_1.threePointArc((0.06123, 0.58165), (0.07225, 0.57424))
loop_1 = loop_1.lineTo(0.08487, 0.5654)
loop_1 = loop_1.lineTo(0.12149, 0.54212)
loop_1 = loop_1.lineTo(0.13371, 0.53373)
loop_1 = loop_1.threePointArc((0.14218, 0.5283), (0.15038, 0.52321))
loop_1 = loop_1.lineTo(0.19229, 0.4995)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_40_interval_0.stl')