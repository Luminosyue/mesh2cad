import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.32711, -0.72642)
loop_1 = loop_1.threePointArc((0.32651, -0.73457), (0.32578, -0.74305))
loop_1 = loop_1.lineTo(0.28499, -0.77471)
loop_1 = loop_1.threePointArc((0.27715, -0.77471), (0.26899, -0.77463))
loop_1 = loop_1.threePointArc((0.25993, -0.7721), (0.25272, -0.77024))
loop_1 = loop_1.lineTo(0.24144, -0.76322)
loop_1 = loop_1.threePointArc((0.23239, -0.75114), (0.22893, -0.74348))
loop_1 = loop_1.threePointArc((0.22824, -0.73402), (0.22746, -0.72642))
loop_1 = loop_1.threePointArc((0.22948, -0.71727), (0.23096, -0.70978))
loop_1 = loop_1.lineTo(0.24556, -0.69422)
loop_1 = loop_1.threePointArc((0.26193, -0.68859), (0.26933, -0.68696))
loop_1 = loop_1.threePointArc((0.27837, -0.68697), (0.28615, -0.68708))
loop_1 = loop_1.lineTo(0.32487, -0.71117)
loop_1 = loop_1.threePointArc((0.32586, -0.71825), (0.32691, -0.72503))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_27_interval_0.stl')