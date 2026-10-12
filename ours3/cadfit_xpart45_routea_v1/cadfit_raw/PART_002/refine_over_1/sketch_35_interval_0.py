import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.07571, 0.42156, -0.10257), normal=(0.56354, -0.82609, 0.00013), xDir=(-0.82609, -0.56354, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.21332, 0.66753)
loop_1 = loop_1.lineTo(0.15956, 0.66753)
loop_1 = loop_1.lineTo(0.14528, 0.66753)
loop_1 = loop_1.lineTo(0.05229, 0.66753)
loop_1 = loop_1.lineTo(0.07014, 0.65461)
loop_1 = loop_1.lineTo(0.08195, 0.6478)
loop_1 = loop_1.threePointArc((0.09405, 0.63947), (0.10584, 0.63174))
loop_1 = loop_1.lineTo(0.11676, 0.62144)
loop_1 = loop_1.lineTo(0.1302, 0.61242)
loop_1 = loop_1.lineTo(0.15064, 0.59333)
loop_1 = loop_1.lineTo(0.1593, 0.58256)
loop_1 = loop_1.lineTo(0.17574, 0.55912)
loop_1 = loop_1.lineTo(0.1915, 0.53838)
loop_1 = loop_1.lineTo(0.19664, 0.52794)
loop_1 = loop_1.lineTo(0.20154, 0.51687)
loop_1 = loop_1.threePointArc((0.20936, 0.50025), (0.21336, 0.49129))
loop_1 = loop_1.lineTo(0.21332, 0.66455)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_35_interval_0.stl')