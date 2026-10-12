import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.77063, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10805, -0.68318)
loop_1 = loop_1.lineTo(0.10824, -0.79244)
loop_1 = loop_1.lineTo(0.29157, -0.79237)
loop_1 = loop_1.threePointArc((0.27523, -0.78799), (0.25845, -0.78334))
loop_1 = loop_1.lineTo(0.23875, -0.76996)
loop_1 = loop_1.lineTo(0.21192, -0.74554)
loop_1 = loop_1.lineTo(0.20183, -0.73212)
loop_1 = loop_1.threePointArc((0.1968, -0.72457), (0.19186, -0.71652))
loop_1 = loop_1.lineTo(0.18463, -0.70535)
loop_1 = loop_1.lineTo(0.15483, -0.68709)
loop_1 = loop_1.lineTo(0.17519, -0.69944)
loop_1 = loop_1.lineTo(0.14766, -0.68416)
loop_1 = loop_1.lineTo(0.12554, -0.68398)
loop_1 = loop_1.lineTo(0.11416, -0.68348)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.43)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_28_interval_0.stl')