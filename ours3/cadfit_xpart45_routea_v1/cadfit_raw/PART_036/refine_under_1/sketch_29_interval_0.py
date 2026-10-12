import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2605, 0.14956, -0.08976), normal=(0.04007, -0.7737, -0.63229), xDir=(-0.99866, -0.05172, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.21326, 0.06439)
loop_1 = loop_1.threePointArc((-1.20469, 0.06376), (-1.19577, 0.063))
loop_1 = loop_1.lineTo(-1.17928, 0.05137)
loop_1 = loop_1.threePointArc((-1.17442, 0.04318), (-1.17292, 0.0396))
loop_1 = loop_1.lineTo(-1.17232, 0.02869)
loop_1 = loop_1.lineTo(-1.24002, 0.02876)
loop_1 = loop_1.threePointArc((-1.24069, 0.03684), (-1.2413, 0.04427))
loop_1 = loop_1.lineTo(-1.22935, 0.05804)
loop_1 = loop_1.lineTo(-1.21404, 0.0641)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_29_interval_0.stl')