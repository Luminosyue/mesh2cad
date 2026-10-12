import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.76694, 0.05866, -0.06593), normal=(-0.99473, -0.10252, -0.0), xDir=(-0.10252, 0.99473, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.14592, -0.23805)
loop_1 = loop_1.lineTo(0.28718, -0.23805)
loop_1 = loop_1.lineTo(0.27644, -0.24131)
loop_1 = loop_1.lineTo(0.23846, -0.25354)
loop_1 = loop_1.lineTo(0.22321, -0.25897)
loop_1 = loop_1.lineTo(0.19887, -0.25975)
loop_1 = loop_1.lineTo(0.17482, -0.26715)
loop_1 = loop_1.lineTo(0.15546, -0.26694)
loop_1 = loop_1.lineTo(0.12643, -0.27139)
loop_1 = loop_1.lineTo(0.11206, -0.27123)
loop_1 = loop_1.lineTo(0.07804, -0.27373)
loop_1 = loop_1.lineTo(0.06432, -0.27366)
loop_1 = loop_1.lineTo(-0.01298, -0.27533)
loop_1 = loop_1.lineTo(-0.06155, -0.27231)
loop_1 = loop_1.lineTo(-0.10495, -0.25891)
loop_1 = loop_1.lineTo(-0.13577, -0.24189)
loop_1 = loop_1.lineTo(-0.14592, -0.23805)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.48)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_31_interval_0.stl')