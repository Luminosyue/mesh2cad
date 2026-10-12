import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05072, -0.06086, -0.02216), normal=(-0.02791, 0.62791, -0.77778), xDir=(0.99901, 0.0444, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.92821, -0.08911)
loop_1 = loop_1.lineTo(0.93484, -0.09947)
loop_1 = loop_1.lineTo(0.94189, -0.10956)
loop_1 = loop_1.lineTo(0.94515, -0.13179)
loop_1 = loop_1.threePointArc((0.94312, -0.14236), (0.94109, -0.15187))
loop_1 = loop_1.threePointArc((0.93477, -0.16269), (0.92955, -0.17007))
loop_1 = loop_1.lineTo(0.91498, -0.17858)
loop_1 = loop_1.threePointArc((0.90556, -0.17875), (0.89991, -0.17767))
loop_1 = loop_1.lineTo(0.88322, -0.16703)
loop_1 = loop_1.lineTo(0.8737, -0.15698)
loop_1 = loop_1.lineTo(0.86763, -0.14016)
loop_1 = loop_1.lineTo(0.87473, -0.11323)
loop_1 = loop_1.threePointArc((0.88279, -0.10144), (0.89078, -0.09005))
loop_1 = loop_1.lineTo(0.92821, -0.08911)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_1_interval_0.stl')