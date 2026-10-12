import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.34229), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.48485, 0.69999)
loop_1 = loop_1.threePointArc((0.49155, 0.69134), (0.49815, 0.68205))
loop_1 = loop_1.threePointArc((0.50459, 0.67303), (0.51081, 0.66352))
loop_1 = loop_1.threePointArc((0.51703, 0.65446), (0.52296, 0.64488))
loop_1 = loop_1.lineTo(0.53981, 0.61794)
loop_1 = loop_1.lineTo(0.56038, 0.57898)
loop_1 = loop_1.lineTo(0.577, 0.54561)
loop_1 = loop_1.threePointArc((0.57975, 0.53818), (0.58218, 0.53049))
loop_1 = loop_1.lineTo(0.58882, 0.51012)
loop_1 = loop_1.lineTo(0.58882, 0.7)
loop_1 = loop_1.lineTo(0.48503, 0.7)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.66)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_48_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_48_interval_0.stl')