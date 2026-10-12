import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.49818, -0.20021, 0.03135), normal=(0.00466, -0.99999, 1e-05), xDir=(-0.99999, -0.00466, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10323, -0.58781)
loop_1 = loop_1.lineTo(0.10344, -0.70472)
loop_1 = loop_1.lineTo(0.1214, -0.69271)
loop_1 = loop_1.lineTo(0.14293, -0.66779)
loop_1 = loop_1.threePointArc((0.14946, -0.65227), (0.15337, -0.64116))
loop_1 = loop_1.threePointArc((0.15274, -0.63081), (0.15195, -0.62218))
loop_1 = loop_1.threePointArc((0.13821, -0.6041), (0.12484, -0.59274))
loop_1 = loop_1.threePointArc((0.11447, -0.59034), (0.10459, -0.58811))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_32_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_32_interval_1.stl')