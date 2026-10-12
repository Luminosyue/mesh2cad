import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00721, 0.19683, -0.1717), normal=(0.04569, -0.99792, 0.04543), xDir=(-0.99895, -0.04574, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.26259, 0.02846)
loop_1 = loop_1.lineTo(0.1116, 0.02846)
loop_1 = loop_1.threePointArc((0.11155, 0.01021), (0.11156, -0.00714))
loop_1 = loop_1.lineTo(0.1138, -0.02566)
loop_1 = loop_1.lineTo(0.1428, -0.02552)
loop_1 = loop_1.lineTo(0.17684, -0.02625)
loop_1 = loop_1.lineTo(0.26549, -0.02632)
loop_1 = loop_1.lineTo(0.26556, -0.00385)
loop_1 = loop_1.threePointArc((0.2652, 0.00399), (0.26484, 0.00963))
loop_1 = loop_1.threePointArc((0.26453, 0.01791), (0.26429, 0.024))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_15_interval_0.stl')