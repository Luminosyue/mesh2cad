import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.96295, -0.08847, -0.1126), normal=(-0.99971, 0.02147, -0.01116), xDir=(0.02147, 0.99977, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.11266, -0.13533)
loop_1 = loop_1.lineTo(0.07195, -0.10022)
loop_1 = loop_1.threePointArc((0.06272, -0.11074), (0.05436, -0.12027))
loop_1 = loop_1.lineTo(0.05783, -0.13533)
loop_1 = loop_1.lineTo(0.11187, -0.13533)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_11_interval_0.stl')