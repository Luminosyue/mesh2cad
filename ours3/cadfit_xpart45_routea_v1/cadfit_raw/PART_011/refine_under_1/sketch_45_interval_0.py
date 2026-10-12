import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00236, 0.83508, -0.0065), normal=(-0.00028, -0.99948, -0.03231), xDir=(-1.0, 0.00028, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.40294, 0.10573)
loop_1 = loop_1.threePointArc((0.4048, 0.09716), (0.40667, 0.08822))
loop_1 = loop_1.lineTo(0.41198, 0.04009)
loop_1 = loop_1.lineTo(0.41192, 0.02827)
loop_1 = loop_1.lineTo(0.41348, -0.00804)
loop_1 = loop_1.threePointArc((0.41323, -0.02971), (0.41343, -0.04802))
loop_1 = loop_1.lineTo(0.41332, -0.05896)
loop_1 = loop_1.lineTo(0.41277, -0.07288)
loop_1 = loop_1.threePointArc((0.41279, -0.09914), (0.41296, -0.12184))
loop_1 = loop_1.lineTo(0.4106, -0.15243)
loop_1 = loop_1.lineTo(0.40302, 0.10305)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_45_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_45_interval_0.stl')