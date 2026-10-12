import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.1, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.18962, -0.10238)
loop_1 = loop_1.threePointArc((0.19598, -0.10954), (0.20036, -0.11564))
loop_1 = loop_1.lineTo(0.20409, -0.14272)
loop_1 = loop_1.lineTo(0.18952, -0.15933)
loop_1 = loop_1.lineTo(0.17024, -0.1656)
loop_1 = loop_1.lineTo(0.16129, -0.14666)
loop_1 = loop_1.lineTo(0.14202, -0.14202)
loop_1 = loop_1.lineTo(0.14821, -0.1313)
loop_1 = loop_1.threePointArc((0.16058, -0.12334), (0.16326, -0.12117))
loop_1 = loop_1.lineTo(0.18123, -0.10839)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_17_interval_0.stl')