import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00047, -0.10409, 0.1791), normal=(-0.01537, 0.37157, -0.92828), xDir=(0.0, -0.92839, -0.37162))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.09363, 0.1702)
loop_1 = loop_1.threePointArc((0.09234, 0.15493), (0.09064, 0.13906))
loop_1 = loop_1.threePointArc((0.08958, 0.12172), (0.08905, 0.10761))
loop_1 = loop_1.threePointArc((0.08831, 0.09029), (0.08806, 0.07623))
loop_1 = loop_1.lineTo(0.0875, 0.06186)
loop_1 = loop_1.lineTo(0.0868, 0.04158)
loop_1 = loop_1.lineTo(0.08605, 0.02979)
loop_1 = loop_1.threePointArc((0.08581, 0.01962), (0.08542, 0.01201))
loop_1 = loop_1.threePointArc((0.08498, 0.11056), (0.08404, 0.20258))
loop_1 = loop_1.lineTo(0.0834, 0.27857)
loop_1 = loop_1.lineTo(0.09363, 0.1702)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_3_interval_0.stl')