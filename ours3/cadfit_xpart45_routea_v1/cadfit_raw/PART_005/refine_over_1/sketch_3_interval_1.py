import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05512, 0.24, 0.11488), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.95115, -0.03198)
loop_1 = loop_1.lineTo(0.951, 0.2409)
loop_1 = loop_1.lineTo(0.94757, 0.21472)
loop_1 = loop_1.lineTo(0.9413, 0.19532)
loop_1 = loop_1.lineTo(0.9281, 0.16287)
loop_1 = loop_1.lineTo(0.91482, 0.14613)
loop_1 = loop_1.lineTo(0.89542, 0.12781)
loop_1 = loop_1.lineTo(0.87621, 0.1111)
loop_1 = loop_1.lineTo(0.87967, 0.09166)
loop_1 = loop_1.lineTo(0.88894, 0.05927)
loop_1 = loop_1.lineTo(0.90576, 0.0484)
loop_1 = loop_1.lineTo(0.93973, 0.01598)
loop_1 = loop_1.lineTo(0.94635, 0.00407)
loop_1 = loop_1.threePointArc((0.94889, -0.01356), (0.95111, -0.03197))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_3_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_3_interval_1.stl')