import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.18), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17665, -0.98263)
loop_1 = loop_1.lineTo(0.15696, -0.96838)
loop_1 = loop_1.lineTo(0.14942, -0.95086)
loop_1 = loop_1.lineTo(0.15289, -0.93362)
loop_1 = loop_1.lineTo(0.17086, -0.92143)
loop_1 = loop_1.lineTo(0.21674, -0.91879)
loop_1 = loop_1.lineTo(0.22797, -0.93175)
loop_1 = loop_1.lineTo(0.22895, -0.95659)
loop_1 = loop_1.lineTo(0.22306, -0.96861)
loop_1 = loop_1.threePointArc((0.20763, -0.97938), (0.20117, -0.98169))
loop_1 = loop_1.threePointArc((0.18915, -0.98213), (0.17673, -0.98263))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_70_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_70_interval_0.stl')