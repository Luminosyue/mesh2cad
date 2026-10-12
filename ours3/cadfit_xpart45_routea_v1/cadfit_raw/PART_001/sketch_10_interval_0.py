import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02089, 0.16662, 0.10305), normal=(0.5328, 0.00029, -0.84624), xDir=(0.00054, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.93059, 0.03279)
loop_1 = loop_1.threePointArc((0.9335, 0.02738), (0.93636, 0.02222))
loop_1 = loop_1.lineTo(0.93601, 0.00814)
loop_1 = loop_1.lineTo(0.93322, -0.00258)
loop_1 = loop_1.lineTo(0.87463, -0.03528)
loop_1 = loop_1.lineTo(0.86521, -0.02062)
loop_1 = loop_1.lineTo(0.85468, -0.01476)
loop_1 = loop_1.threePointArc((0.8489, -0.01494), (0.84432, -0.01502))
loop_1 = loop_1.threePointArc((0.83802, -0.01472), (0.83349, -0.0144))
loop_1 = loop_1.lineTo(0.80254, 0.01109)
loop_1 = loop_1.threePointArc((0.80764, 0.01309), (0.81298, 0.01512))
loop_1 = loop_1.lineTo(0.83725, 0.0162)
loop_1 = loop_1.lineTo(0.89832, 0.03682)
loop_1 = loop_1.threePointArc((0.90766, 0.0372), (0.9174, 0.03749))
loop_1 = loop_1.lineTo(0.93059, 0.03279)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_10_interval_0.stl')