import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.82087, 0.04287, 0.05283), normal=(0.99097, 0.13358, 0.01143), xDir=(0.13359, -0.99104, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.38064, 0.03495)
loop_1 = loop_1.lineTo(0.37448, -0.19457)
loop_1 = loop_1.lineTo(0.38502, -0.18328)
loop_1 = loop_1.lineTo(0.3837, -0.14473)
loop_1 = loop_1.threePointArc((0.38405, -0.12019), (0.38451, -0.09687))
loop_1 = loop_1.lineTo(0.38336, -0.08238)
loop_1 = loop_1.lineTo(0.37981, -0.05228)
loop_1 = loop_1.threePointArc((0.38044, -0.01503), (0.38058, 0.01842))
loop_1 = loop_1.lineTo(0.38064, 0.03495)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_35_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_35_interval_1.stl')