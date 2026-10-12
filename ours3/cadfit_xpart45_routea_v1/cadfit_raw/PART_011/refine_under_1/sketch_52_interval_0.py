import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.8099, 0.1325, 0.00696), normal=(-0.97687, -0.21308, -0.01812), xDir=(-0.21311, 0.97703, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.37218, 0.20801)
loop_1 = loop_1.lineTo(-0.38612, -0.14879)
loop_1 = loop_1.lineTo(-0.39708, -0.13877)
loop_1 = loop_1.lineTo(-0.39527, -0.09066)
loop_1 = loop_1.lineTo(-0.39493, -0.04255)
loop_1 = loop_1.lineTo(-0.39192, 0.00205)
loop_1 = loop_1.lineTo(-0.38941, 0.05726)
loop_1 = loop_1.threePointArc((-0.386, 0.10624), (-0.38421, 0.1499))
loop_1 = loop_1.threePointArc((-0.38177, 0.17628), (-0.38012, 0.19802))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_52_interval_0.stl')