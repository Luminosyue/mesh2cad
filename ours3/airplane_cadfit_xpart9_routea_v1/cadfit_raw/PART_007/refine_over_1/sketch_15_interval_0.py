import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04055, -0.23159, 0.05315), normal=(-0.26995, -0.52965, -0.80411), xDir=(-0.89096, 0.45409, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.03694, -0.01158)
loop_1 = loop_1.lineTo(1.03716, 0.00131)
loop_1 = loop_1.lineTo(0.6087, -0.07134)
loop_1 = loop_1.lineTo(-0.19536, -0.19725)
loop_1 = loop_1.lineTo(-0.10007, -0.18769)
loop_1 = loop_1.lineTo(-0.08955, -0.18618)
loop_1 = loop_1.threePointArc((-0.08025, -0.18756), (-0.07628, -0.18913))
loop_1 = loop_1.threePointArc((0.13595, -0.16456), (0.34754, -0.14093))
loop_1 = loop_1.threePointArc((0.43558, -0.13308), (0.51319, -0.12496))
loop_1 = loop_1.threePointArc((0.60938, -0.11531), (0.70012, -0.10217))
loop_1 = loop_1.threePointArc((0.80833, -0.08818), (0.9214, -0.07692))
loop_1 = loop_1.threePointArc((0.9755, -0.06671), (1.01667, -0.04507))
loop_1 = loop_1.threePointArc((1.02937, -0.02897), (1.03684, -0.01162))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.13)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_15_interval_0.stl')