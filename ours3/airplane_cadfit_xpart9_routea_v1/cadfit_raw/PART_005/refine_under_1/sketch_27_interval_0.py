import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02136, -0.58523, 0.15975), normal=(-0.02357, 0.10143, -0.99456), xDir=(0.0, -0.99484, -0.10146))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.46362, -0.01231)
loop_1 = loop_1.threePointArc((-0.46424, -0.02211), (-0.46488, -0.03231))
loop_1 = loop_1.lineTo(0.06616, -0.0323)
loop_1 = loop_1.lineTo(0.1092, -0.03229)
loop_1 = loop_1.lineTo(0.12416, -0.03196)
loop_1 = loop_1.lineTo(0.14502, -0.03032)
loop_1 = loop_1.lineTo(0.16747, -0.03212)
loop_1 = loop_1.lineTo(0.22797, -0.03229)
loop_1 = loop_1.threePointArc((0.23676, -0.01884), (0.23644, -0.01489))
loop_1 = loop_1.lineTo(-0.22356, -0.01286)
loop_1 = loop_1.lineTo(-0.46117, -0.01231)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_27_interval_0.stl')