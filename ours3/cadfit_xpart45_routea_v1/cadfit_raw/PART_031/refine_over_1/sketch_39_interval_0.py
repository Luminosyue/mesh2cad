import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.83096, -0.46339, 0.02895), normal=(0.91138, 0.41151, -0.00634), xDir=(0.41152, -0.9114, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28936, -0.0878)
loop_1 = loop_1.lineTo(0.29457, -0.43798)
loop_1 = loop_1.lineTo(0.24316, -0.43798)
loop_1 = loop_1.lineTo(0.26095, -0.42897)
loop_1 = loop_1.lineTo(0.26293, -0.40999)
loop_1 = loop_1.lineTo(0.2654, -0.37918)
loop_1 = loop_1.lineTo(0.26515, -0.36489)
loop_1 = loop_1.lineTo(0.26771, -0.32938)
loop_1 = loop_1.threePointArc((0.26694, -0.30231), (0.26608, -0.27959))
loop_1 = loop_1.lineTo(0.27367, -0.23443)
loop_1 = loop_1.lineTo(0.27765, -0.1849)
loop_1 = loop_1.threePointArc((0.28141, -0.1634), (0.28424, -0.14484))
loop_1 = loop_1.lineTo(0.2859, -0.1302)
loop_1 = loop_1.threePointArc((0.28768, -0.10755), (0.28933, -0.08818))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_39_interval_0.stl')