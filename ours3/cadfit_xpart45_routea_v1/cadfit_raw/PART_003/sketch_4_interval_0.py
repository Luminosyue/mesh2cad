import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00836, 0.12792, 0.03148), normal=(-0.64445, -0.02737, -0.76416), xDir=(-0.04243, 0.9991, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.09111, 0.02894)
loop_1 = loop_1.lineTo(-1.08068, 0.02925)
loop_1 = loop_1.lineTo(-1.04275, 0.01946)
loop_1 = loop_1.lineTo(-1.0215, 0.01638)
loop_1 = loop_1.lineTo(-1.00979, 0.01785)
loop_1 = loop_1.threePointArc((-1.00044, 0.01875), (-0.99069, 0.01951))
loop_1 = loop_1.lineTo(-0.98721, -0.02035)
loop_1 = loop_1.threePointArc((-0.9959, -0.01981), (-1.00495, -0.01912))
loop_1 = loop_1.lineTo(-1.02041, -0.01716)
loop_1 = loop_1.lineTo(-1.03218, -0.01673)
loop_1 = loop_1.lineTo(-1.04535, -0.02364)
loop_1 = loop_1.lineTo(-1.09209, -0.03424)
loop_1 = loop_1.lineTo(-1.11379, -0.03701)
loop_1 = loop_1.lineTo(-1.12238, -0.02566)
loop_1 = loop_1.lineTo(-1.09111, 0.02894)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_003/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_003/sketch_4_interval_0.stl')