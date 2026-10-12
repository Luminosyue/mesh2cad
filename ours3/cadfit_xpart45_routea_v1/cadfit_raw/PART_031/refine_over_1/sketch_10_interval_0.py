import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.70536, -0.60754, 0.02649), normal=(0.83849, 0.54491, -0.00028), xDir=(0.54491, -0.83849, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28871, -0.33064)
loop_1 = loop_1.lineTo(0.28719, -0.35758)
loop_1 = loop_1.lineTo(0.28743, -0.38205)
loop_1 = loop_1.threePointArc((0.27519, -0.40732), (0.26327, -0.43185))
loop_1 = loop_1.lineTo(0.24496, -0.43976)
loop_1 = loop_1.lineTo(0.28862, -0.44085)
loop_1 = loop_1.lineTo(0.28871, -0.33209)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_10_interval_0.stl')