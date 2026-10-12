import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.5727, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.18596, -0.48706)
loop_1 = loop_1.threePointArc((0.20202, -0.46415), (0.21658, -0.44158))
loop_1 = loop_1.threePointArc((0.22703, -0.42588), (0.23787, -0.40999))
loop_1 = loop_1.lineTo(0.68498, -0.5236)
loop_1 = loop_1.lineTo(0.14979, -0.52885)
loop_1 = loop_1.threePointArc((0.1578, -0.52107), (0.16432, -0.51304))
loop_1 = loop_1.threePointArc((0.17506, -0.50023), (0.18592, -0.48715))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_77_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_77_interval_0.stl')