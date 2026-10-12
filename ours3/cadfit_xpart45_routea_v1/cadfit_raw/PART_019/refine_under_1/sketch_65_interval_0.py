import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.75, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.98298, 0.17905)
loop_1 = loop_1.threePointArc((0.98459, 0.15254), (0.98585, 0.1249))
loop_1 = loop_1.lineTo(0.98359, 0.06233)
loop_1 = loop_1.lineTo(0.98581, -0.00372)
loop_1 = loop_1.threePointArc((0.98593, -0.03206), (0.98637, -0.05897))
loop_1 = loop_1.threePointArc((0.98336, -0.08447), (0.98143, -0.10873))
loop_1 = loop_1.threePointArc((0.97741, -0.14641), (0.97414, -0.18234))
loop_1 = loop_1.lineTo(0.95896, -0.24682)
loop_1 = loop_1.threePointArc((0.96342, -0.22269), (0.96807, -0.19429))
loop_1 = loop_1.lineTo(0.98394, -0.0625)
loop_1 = loop_1.threePointArc((0.98393, -0.03845), (0.98359, -0.01564))
loop_1 = loop_1.threePointArc((0.98216, 0.02119), (0.97982, 0.05623))
loop_1 = loop_1.threePointArc((0.97983, 0.0614), (0.98034, 0.06645))
loop_1 = loop_1.lineTo(0.98286, 0.10492)
loop_1 = loop_1.lineTo(0.98373, 0.14556)
loop_1 = loop_1.lineTo(0.98307, 0.17878)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.49)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_65_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_65_interval_0.stl')