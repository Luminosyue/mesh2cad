import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.036, 0.08759, 0.95595), normal=(-0.00132, -0.00278, -1.0), xDir=(0.0, -1.0, 0.00278))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.70064, -0.11586)
loop_1 = loop_1.lineTo(-0.70419, -0.09196)
loop_1 = loop_1.threePointArc((-0.70681, -0.06596), (-0.70861, -0.04188))
loop_1 = loop_1.lineTo(-0.70966, -0.02726)
loop_1 = loop_1.lineTo(-0.7117, 0.03505)
loop_1 = loop_1.lineTo(-0.71194, 0.0699)
loop_1 = loop_1.threePointArc((-0.7102, 0.10278), (-0.70907, 0.13158))
loop_1 = loop_1.threePointArc((-0.7051, 0.16196), (-0.70093, 0.19053))
loop_1 = loop_1.lineTo(-0.70065, -0.11282)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.9)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_7_interval_0.stl')