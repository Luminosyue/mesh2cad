import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.23014, -0.028, -0.26695), normal=(0.02357, -0.65303, 0.75696), xDir=(-0.99935, -0.03607, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.39326, -0.07614)
loop_1 = loop_1.lineTo(0.35512, -0.0761)
loop_1 = loop_1.lineTo(0.35582, -0.06014)
loop_1 = loop_1.threePointArc((0.35811, -0.05377), (0.36062, -0.04718))
loop_1 = loop_1.lineTo(0.38156, -0.02944)
loop_1 = loop_1.lineTo(0.39468, -0.02691)
loop_1 = loop_1.threePointArc((0.39442, -0.03623), (0.39425, -0.04444))
loop_1 = loop_1.lineTo(0.39377, -0.06354)
loop_1 = loop_1.lineTo(0.3933, -0.07522)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_14_interval_0.stl')