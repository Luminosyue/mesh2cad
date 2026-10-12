import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.30754, 0.85572, 0.01028), normal=(0.51752, -0.85527, -0.02629), xDir=(-0.85556, -0.5177, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30849, 0.26896)
loop_1 = loop_1.lineTo(-0.24866, 0.25219)
loop_1 = loop_1.lineTo(-0.2293, -0.16526)
loop_1 = loop_1.lineTo(0.30967, -0.16526)
loop_1 = loop_1.threePointArc((0.30964, 0.00203), (0.30879, 0.15338))
loop_1 = loop_1.lineTo(0.30853, 0.25933)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.83)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_18_interval_0.stl')