import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.17595, -0.24314, -0.09416), normal=(-0.02357, 0.65303, -0.75696), xDir=(0.99935, 0.03607, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.79445, -0.42036)
loop_1 = loop_1.lineTo(0.80682, -0.42712)
loop_1 = loop_1.lineTo(0.81705, -0.44152)
loop_1 = loop_1.lineTo(0.82145, -0.45496)
loop_1 = loop_1.lineTo(0.82494, -0.46551)
loop_1 = loop_1.lineTo(0.82323, -0.48162)
loop_1 = loop_1.threePointArc((0.81535, -0.49719), (0.80897, -0.50574))
loop_1 = loop_1.lineTo(0.79072, -0.51274)
loop_1 = loop_1.threePointArc((0.78265, -0.51196), (0.77425, -0.51109))
loop_1 = loop_1.threePointArc((0.76466, -0.50489), (0.7565, -0.49963))
loop_1 = loop_1.lineTo(0.74991, -0.48947)
loop_1 = loop_1.threePointArc((0.74724, -0.4785), (0.7445, -0.46802))
loop_1 = loop_1.threePointArc((0.74668, -0.45553), (0.74849, -0.44479))
loop_1 = loop_1.threePointArc((0.75198, -0.43854), (0.75469, -0.43367))
loop_1 = loop_1.lineTo(0.7732, -0.42039)
loop_1 = loop_1.lineTo(0.79445, -0.42036)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_4_interval_0.stl')