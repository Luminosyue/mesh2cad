import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.55403, -0.54687, -0.00501), normal=(-0.78932, -0.61398, 0.00017), xDir=(-0.61398, 0.78932, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.26065, 0.13962)
loop_1 = loop_1.lineTo(0.28706, 0.1173)
loop_1 = loop_1.threePointArc((0.29812, 0.10775), (0.30797, 0.09932))
loop_1 = loop_1.lineTo(0.31375, 0.06698)
loop_1 = loop_1.lineTo(0.31372, 0.13962)
loop_1 = loop_1.lineTo(0.26175, 0.13962)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.13)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_24_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_24_interval_1.stl')