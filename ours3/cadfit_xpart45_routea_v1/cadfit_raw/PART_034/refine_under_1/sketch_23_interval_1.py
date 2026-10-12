import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38508, 0.81761, 0.03448), normal=(-0.45204, 0.892, -0.00016), xDir=(0.892, 0.45204, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.29394, 0.16411)
loop_1 = loop_1.lineTo(0.29405, -0.15421)
loop_1 = loop_1.threePointArc((0.29469, -0.12587), (0.29457, -0.10328))
loop_1 = loop_1.threePointArc((0.29648, -0.0777), (0.29849, -0.05432))
loop_1 = loop_1.lineTo(0.29983, -0.02828)
loop_1 = loop_1.lineTo(0.29828, -0.00536)
loop_1 = loop_1.threePointArc((0.29917, 0.00737), (0.29992, 0.01753))
loop_1 = loop_1.lineTo(0.31388, 0.09256)
loop_1 = loop_1.lineTo(0.31339, 0.12696)
loop_1 = loop_1.lineTo(0.3116, 0.14152)
loop_1 = loop_1.lineTo(0.29592, 0.16152)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_23_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_23_interval_1.stl')