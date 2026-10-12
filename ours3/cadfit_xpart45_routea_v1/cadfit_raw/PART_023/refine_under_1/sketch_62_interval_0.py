import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.46312, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10811, 0.93772)
loop_1 = loop_1.lineTo(0.10883, 0.58364)
loop_1 = loop_1.lineTo(0.11611, 0.60383)
loop_1 = loop_1.threePointArc((0.122, 0.61075), (0.12709, 0.61755))
loop_1 = loop_1.lineTo(0.13593, 0.62914)
loop_1 = loop_1.threePointArc((0.13514, 0.63683), (0.13387, 0.64391))
loop_1 = loop_1.lineTo(0.1319, 0.65531)
loop_1 = loop_1.lineTo(0.12203, 0.68113)
loop_1 = loop_1.threePointArc((0.11994, 0.69396), (0.11822, 0.70714))
loop_1 = loop_1.threePointArc((0.1181, 0.72963), (0.11666, 0.75092))
loop_1 = loop_1.lineTo(0.11162, 0.81817)
loop_1 = loop_1.lineTo(0.11049, 0.83622)
loop_1 = loop_1.threePointArc((0.10993, 0.85245), (0.10968, 0.86911))
loop_1 = loop_1.threePointArc((0.10983, 0.89116), (0.10954, 0.9121))
loop_1 = loop_1.lineTo(0.10958, 0.93558)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_62_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_62_interval_0.stl')