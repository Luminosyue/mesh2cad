import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.13069, -0.93026, 0.04684), normal=(-0.14078, 0.98944, 0.0345), xDir=(0.99003, 0.14087, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.36041, 0.19765)
loop_1 = loop_1.lineTo(0.40242, 0.19765)
loop_1 = loop_1.lineTo(0.40923, 0.17585)
loop_1 = loop_1.threePointArc((0.40535, 0.15165), (0.40079, 0.12654))
loop_1 = loop_1.lineTo(0.39959, 0.09004)
loop_1 = loop_1.lineTo(0.40197, 0.03914)
loop_1 = loop_1.lineTo(0.40122, 0.02762)
loop_1 = loop_1.threePointArc((0.39929, -0.00629), (0.39632, -0.04153))
loop_1 = loop_1.lineTo(0.39558, -0.05256)
loop_1 = loop_1.lineTo(0.38685, -0.18493)
loop_1 = loop_1.lineTo(0.34008, -0.17161)
loop_1 = loop_1.lineTo(0.33913, -0.2126)
loop_1 = loop_1.lineTo(-0.33411, -0.2126)
loop_1 = loop_1.lineTo(-0.33205, 0.19765)
loop_1 = loop_1.lineTo(0.33966, 0.19765)
loop_1 = loop_1.lineTo(0.36041, 0.19765)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.8)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_39_interval_0.stl')