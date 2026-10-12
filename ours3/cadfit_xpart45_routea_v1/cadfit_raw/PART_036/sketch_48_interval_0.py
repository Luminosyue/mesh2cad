import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.19259), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.16195, -0.95103)
loop_1 = loop_1.threePointArc((0.16563, -0.96005), (0.16932, -0.96865))
loop_1 = loop_1.threePointArc((0.17444, -0.97367), (0.17935, -0.97835))
loop_1 = loop_1.lineTo(0.19003, -0.98336)
loop_1 = loop_1.lineTo(0.21411, -0.98206)
loop_1 = loop_1.threePointArc((0.22113, -0.97512), (0.22774, -0.96834))
loop_1 = loop_1.lineTo(0.23165, -0.95581)
loop_1 = loop_1.threePointArc((0.23233, -0.94187), (0.23158, -0.93339))
loop_1 = loop_1.threePointArc((0.22702, -0.92444), (0.22254, -0.916))
loop_1 = loop_1.threePointArc((0.20489, -0.90681), (0.19639, -0.90485))
loop_1 = loop_1.lineTo(0.17893, -0.90982)
loop_1 = loop_1.threePointArc((0.16676, -0.92496), (0.16227, -0.93373))
loop_1 = loop_1.lineTo(0.16232, -0.94444)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.43)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_48_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_48_interval_0.stl')