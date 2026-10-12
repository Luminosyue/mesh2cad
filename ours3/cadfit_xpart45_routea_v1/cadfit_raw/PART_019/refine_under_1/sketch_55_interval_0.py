import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.14722, 0.10411, -0.91346), normal=(0.15066, -0.00105, 0.98858), xDir=(-0.0, 1.0, 0.00106))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.68615, -0.36586)
loop_1 = loop_1.lineTo(0.69658, -0.32476)
loop_1 = loop_1.lineTo(0.7065, -0.26444)
loop_1 = loop_1.lineTo(0.70832, -0.2442)
loop_1 = loop_1.lineTo(0.70718, -0.20798)
loop_1 = loop_1.threePointArc((0.70772, -0.17189), (0.70858, -0.14006))
loop_1 = loop_1.threePointArc((0.70885, -0.10292), (0.7099, -0.07125))
loop_1 = loop_1.threePointArc((0.71036, -0.04054), (0.71134, -0.01527))
loop_1 = loop_1.lineTo(0.70961, 0.0086)
loop_1 = loop_1.lineTo(0.71247, 0.04713)
loop_1 = loop_1.lineTo(0.70834, 0.06275)
loop_1 = loop_1.lineTo(0.71121, 0.11322)
loop_1 = loop_1.lineTo(0.71209, 0.1652)
loop_1 = loop_1.lineTo(0.71047, 0.17859)
loop_1 = loop_1.lineTo(0.70237, 0.2252)
loop_1 = loop_1.lineTo(0.68668, 0.27657)
loop_1 = loop_1.lineTo(0.68615, -0.35981)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.85)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_55_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_55_interval_0.stl')