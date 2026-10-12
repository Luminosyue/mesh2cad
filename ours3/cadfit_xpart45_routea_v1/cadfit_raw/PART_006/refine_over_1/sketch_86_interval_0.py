import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.53029), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.14421, 0.98345)
loop_1 = loop_1.threePointArc((-0.15836, 0.98094), (-0.17186, 0.97812))
loop_1 = loop_1.lineTo(-0.1845, 0.97491)
loop_1 = loop_1.lineTo(-0.16751, 0.97844)
loop_1 = loop_1.threePointArc((-0.19629, 0.97146), (-0.2234, 0.96408))
loop_1 = loop_1.lineTo(-0.2646, 0.95289)
loop_1 = loop_1.lineTo(-0.49914, 0.85379)
loop_1 = loop_1.lineTo(-0.48, 0.86689)
loop_1 = loop_1.lineTo(-0.47933, 0.98813)
loop_1 = loop_1.lineTo(-0.1134, 0.98757)
loop_1 = loop_1.lineTo(-0.14098, 0.98419)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_86_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_86_interval_0.stl')