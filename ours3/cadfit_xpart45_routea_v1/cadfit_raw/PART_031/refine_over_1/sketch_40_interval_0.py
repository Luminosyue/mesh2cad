import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0615, 0.53678, 0.38394), normal=(0.00053, 0.0601, 0.99819), xDir=(0.0, 0.99819, -0.0601))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.03772, -0.16795)
loop_1 = loop_1.lineTo(-0.04471, -0.18671)
loop_1 = loop_1.lineTo(-0.05279, -0.19899)
loop_1 = loop_1.lineTo(-0.04821, 0.3248)
loop_1 = loop_1.lineTo(-0.04265, 0.31124)
loop_1 = loop_1.lineTo(-0.02655, 0.27225)
loop_1 = loop_1.lineTo(-0.02191, 0.25653)
loop_1 = loop_1.threePointArc((-0.01705, 0.23838), (-0.01349, 0.22456))
loop_1 = loop_1.lineTo(-0.0088, 0.20697)
loop_1 = loop_1.lineTo(-0.00336, 0.16186)
loop_1 = loop_1.threePointArc((-0.00168, 0.13478), (-0.00044, 0.11206))
loop_1 = loop_1.threePointArc((-0.00035, 0.08507), (-0.00038, 0.06227))
loop_1 = loop_1.lineTo(-0.03226, -0.1521)
loop_1 = loop_1.lineTo(-0.03772, -0.16795)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_40_interval_0.stl')