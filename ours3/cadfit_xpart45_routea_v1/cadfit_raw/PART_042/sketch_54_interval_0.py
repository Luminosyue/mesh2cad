import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.3825), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23523, -0.53046)
loop_1 = loop_1.threePointArc((0.23549, -0.54558), (0.23558, -0.56133))
loop_1 = loop_1.lineTo(0.23549, -0.57908)
loop_1 = loop_1.lineTo(0.23604, -0.59499)
loop_1 = loop_1.lineTo(0.25317, -0.59234)
loop_1 = loop_1.threePointArc((0.25292, -0.57903), (0.25245, -0.56625))
loop_1 = loop_1.threePointArc((0.25231, -0.52631), (0.25194, -0.48811))
loop_1 = loop_1.threePointArc((0.25191, -0.47756), (0.25163, -0.46757))
loop_1 = loop_1.threePointArc((0.25066, -0.45096), (0.25026, -0.44323))
loop_1 = loop_1.lineTo(0.25007, -0.42444)
loop_1 = loop_1.lineTo(0.24669, -0.41048)
loop_1 = loop_1.lineTo(0.23699, -0.42653)
loop_1 = loop_1.threePointArc((0.23679, -0.43862), (0.23677, -0.4501))
loop_1 = loop_1.lineTo(0.2358, -0.47378)
loop_1 = loop_1.threePointArc((0.23567, -0.49382), (0.23526, -0.51455))
loop_1 = loop_1.threePointArc((0.23539, -0.52208), (0.23529, -0.52979))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.65)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_54_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_54_interval_0.stl')