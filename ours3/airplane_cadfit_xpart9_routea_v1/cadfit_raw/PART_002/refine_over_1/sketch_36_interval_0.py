import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.17815, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.22556, 0.1953)
loop_1 = loop_1.lineTo(0.22507, -0.00461)
loop_1 = loop_1.lineTo(0.14995, -0.00434)
loop_1 = loop_1.lineTo(0.15694, 0.00606)
loop_1 = loop_1.lineTo(0.17241, 0.02699)
loop_1 = loop_1.threePointArc((0.176, 0.03455), (0.17918, 0.04176))
loop_1 = loop_1.lineTo(0.18813, 0.06454)
loop_1 = loop_1.lineTo(0.19693, 0.09546)
loop_1 = loop_1.lineTo(0.20032, 0.10659)
loop_1 = loop_1.lineTo(0.20554, 0.12853)
loop_1 = loop_1.threePointArc((0.20898, 0.14005), (0.21192, 0.15104))
loop_1 = loop_1.threePointArc((0.21429, 0.15924), (0.21688, 0.16756))
loop_1 = loop_1.lineTo(0.22547, 0.19492)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_36_interval_0.stl')