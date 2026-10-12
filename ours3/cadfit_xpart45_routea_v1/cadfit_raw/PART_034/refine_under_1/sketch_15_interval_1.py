import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.06217, 0.72225, 0.00934), normal=(-0.06485, 0.99785, -0.00971), xDir=(0.99789, 0.06485, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.40609, 0.15564)
loop_1 = loop_1.lineTo(-0.41329, -0.13376)
loop_1 = loop_1.threePointArc((-0.41521, -0.09375), (-0.41665, -0.05515))
loop_1 = loop_1.lineTo(-0.41753, -0.03763)
loop_1 = loop_1.lineTo(-0.4205, -0.01495)
loop_1 = loop_1.lineTo(-0.42238, 0.00673)
loop_1 = loop_1.lineTo(-0.42335, 0.03401)
loop_1 = loop_1.threePointArc((-0.42256, 0.0576), (-0.42247, 0.07738))
loop_1 = loop_1.lineTo(-0.42065, 0.10452)
loop_1 = loop_1.lineTo(-0.41685, 0.13194)
loop_1 = loop_1.lineTo(-0.40739, 0.15275)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_15_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_15_interval_1.stl')