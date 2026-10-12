import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.41513, 0.00311, -0.01485), normal=(1.0, -0.0, 0.0), xDir=(-0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.74936, 0.17301)
loop_1 = loop_1.threePointArc((0.75064, 0.15109), (0.75184, 0.12825))
loop_1 = loop_1.lineTo(0.75134, 0.07683)
loop_1 = loop_1.threePointArc((0.75213, 0.02612), (0.75261, -0.02326))
loop_1 = loop_1.threePointArc((0.75312, -0.04513), (0.75327, -0.06417))
loop_1 = loop_1.threePointArc((0.75219, -0.09579), (0.75169, -0.12258))
loop_1 = loop_1.lineTo(0.75135, -0.16038)
loop_1 = loop_1.lineTo(0.74739, 0.17781)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_39_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_39_interval_1.stl')