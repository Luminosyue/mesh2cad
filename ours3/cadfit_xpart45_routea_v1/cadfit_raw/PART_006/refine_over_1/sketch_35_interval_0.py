import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.35976, -0.52704, 0.06693), normal=(0.62223, 0.78284, 0.0), xDir=(0.78284, -0.62223, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.32918, -0.40921)
loop_1 = loop_1.threePointArc((-0.32457, -0.41591), (-0.32002, -0.42225))
loop_1 = loop_1.lineTo(-0.28928, -0.46117)
loop_1 = loop_1.lineTo(-0.32918, -0.46243)
loop_1 = loop_1.lineTo(-0.32918, -0.41004)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_35_interval_0.stl')