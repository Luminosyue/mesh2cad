import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.1485, 0.22061, -0.12447), normal=(0.04884, -0.95265, -0.30012), xDir=(-0.99869, -0.0512, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.09153, -0.10526)
loop_1 = loop_1.threePointArc((-1.0829, -0.10858), (-1.07398, -0.11218))
loop_1 = loop_1.lineTo(-1.06053, -0.14132)
loop_1 = loop_1.threePointArc((-1.0599, -0.14948), (-1.05925, -0.15798))
loop_1 = loop_1.lineTo(-1.06027, -0.17231)
loop_1 = loop_1.lineTo(-1.06762, -0.20155)
loop_1 = loop_1.lineTo(-1.0918, -0.22055)
loop_1 = loop_1.lineTo(-1.10725, -0.21853)
loop_1 = loop_1.lineTo(-1.11867, -0.20109)
loop_1 = loop_1.lineTo(-1.12889, -0.16707)
loop_1 = loop_1.lineTo(-1.12172, -0.12035)
loop_1 = loop_1.lineTo(-1.10894, -0.10778)
loop_1 = loop_1.lineTo(-1.09207, -0.10531)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.3)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_9_interval_0.stl')