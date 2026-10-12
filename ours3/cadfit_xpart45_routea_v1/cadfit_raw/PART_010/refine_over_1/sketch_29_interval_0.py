import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.73063, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.39697, -0.51913)
loop_1 = loop_1.lineTo(-0.41672, -0.50931)
loop_1 = loop_1.lineTo(-0.41637, -0.66795)
loop_1 = loop_1.lineTo(-0.29835, -0.66765)
loop_1 = loop_1.lineTo(-0.31548, -0.65373)
loop_1 = loop_1.lineTo(-0.33707, -0.62592)
loop_1 = loop_1.lineTo(-0.36074, -0.59887)
loop_1 = loop_1.lineTo(-0.37178, -0.58037)
loop_1 = loop_1.lineTo(-0.37915, -0.55066)
loop_1 = loop_1.lineTo(-0.38526, -0.52878)
loop_1 = loop_1.threePointArc((-0.39348, -0.52293), (-0.39663, -0.51979))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.71)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_29_interval_0.stl')