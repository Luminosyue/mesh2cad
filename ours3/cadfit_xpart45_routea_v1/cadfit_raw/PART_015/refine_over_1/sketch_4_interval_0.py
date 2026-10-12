import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03469, -0.15005, -0.28887), normal=(-0.00152, -0.05475, 0.9985), xDir=(-0.0, 0.9985, 0.05475))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.89687, 0.51251)
loop_1 = loop_1.lineTo(0.90539, 0.50148)
loop_1 = loop_1.threePointArc((0.91151, 0.49208), (0.91758, 0.48319))
loop_1 = loop_1.lineTo(0.93707, 0.45453)
loop_1 = loop_1.lineTo(0.94944, 0.43247)
loop_1 = loop_1.threePointArc((0.95553, 0.42227), (0.95825, 0.41735))
loop_1 = loop_1.lineTo(0.9583, 0.51252)
loop_1 = loop_1.lineTo(0.89823, 0.51252)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_4_interval_0.stl')