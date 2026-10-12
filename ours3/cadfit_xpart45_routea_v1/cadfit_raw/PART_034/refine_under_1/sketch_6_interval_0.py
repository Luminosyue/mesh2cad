import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.41622, -0.83152, 0.03341), normal=(0.48756, 0.87304, -0.00905), xDir=(0.87308, -0.48758, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.31135, -0.25056)
loop_1 = loop_1.lineTo(0.21078, -0.25373)
loop_1 = loop_1.lineTo(0.18472, -0.25894)
loop_1 = loop_1.lineTo(0.14666, -0.26905)
loop_1 = loop_1.lineTo(0.12858, -0.27)
loop_1 = loop_1.lineTo(0.10561, -0.27252)
loop_1 = loop_1.lineTo(0.07248, -0.27396)
loop_1 = loop_1.lineTo(0.04638, -0.27751)
loop_1 = loop_1.threePointArc((0.00924, -0.27798), (-0.0216, -0.27908))
loop_1 = loop_1.lineTo(-0.0397, -0.27816)
loop_1 = loop_1.lineTo(-0.05401, -0.27855)
loop_1 = loop_1.lineTo(-0.09577, -0.27652)
loop_1 = loop_1.lineTo(-0.14856, -0.27732)
loop_1 = loop_1.threePointArc((-0.16354, -0.27584), (-0.17582, -0.27433))
loop_1 = loop_1.threePointArc((-0.21884, -0.26981), (-0.25505, -0.26652))
loop_1 = loop_1.lineTo(-0.28054, -0.26147)
loop_1 = loop_1.threePointArc((-0.29532, -0.25636), (-0.30956, -0.25163))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.73)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_6_interval_0.stl')