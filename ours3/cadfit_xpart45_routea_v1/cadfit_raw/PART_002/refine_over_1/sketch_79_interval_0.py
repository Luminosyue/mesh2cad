import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.22041, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.04626, 0.99742)
loop_1 = loop_1.lineTo(0.09179, 0.99453)
loop_1 = loop_1.threePointArc((0.10567, 0.99359), (0.11888, 0.99313))
loop_1 = loop_1.lineTo(0.14424, 0.99153)
loop_1 = loop_1.threePointArc((0.15258, 0.99121), (0.16109, 0.99069))
loop_1 = loop_1.lineTo(0.17921, 0.98929)
loop_1 = loop_1.threePointArc((0.1888, 0.98896), (0.19861, 0.98843))
loop_1 = loop_1.threePointArc((0.20752, 0.98797), (0.21494, 0.98727))
loop_1 = loop_1.lineTo(0.23308, 0.98626)
loop_1 = loop_1.threePointArc((0.24634, 0.98464), (0.25998, 0.98282))
loop_1 = loop_1.lineTo(0.25984, 0.99758)
loop_1 = loop_1.lineTo(0.0461, 0.99743)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_79_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_79_interval_0.stl')