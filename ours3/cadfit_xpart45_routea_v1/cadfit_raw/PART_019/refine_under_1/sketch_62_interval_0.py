import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.74237, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.98345, 0.15733)
loop_1 = loop_1.threePointArc((0.98375, 0.13876), (0.98316, 0.11942))
loop_1 = loop_1.threePointArc((0.98297, 0.10742), (0.9824, 0.0952))
loop_1 = loop_1.lineTo(0.97984, 0.05762)
loop_1 = loop_1.lineTo(0.98265, 0.01123)
loop_1 = loop_1.lineTo(0.98386, -0.03044)
loop_1 = loop_1.lineTo(0.98371, -0.06787)
loop_1 = loop_1.lineTo(0.96697, -0.20427)
loop_1 = loop_1.lineTo(0.97417, -0.17811)
loop_1 = loop_1.threePointArc((0.98178, -0.11827), (0.99047, -0.05629))
loop_1 = loop_1.lineTo(0.98819, 0.01063)
loop_1 = loop_1.lineTo(0.98491, 0.06888)
loop_1 = loop_1.lineTo(0.98635, 0.12998)
loop_1 = loop_1.lineTo(0.98352, 0.15709)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.48)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_62_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_62_interval_0.stl')