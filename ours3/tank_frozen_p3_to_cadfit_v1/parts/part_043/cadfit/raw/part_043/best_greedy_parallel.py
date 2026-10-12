import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.3, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.33333, 0.39807)
loop_1 = loop_1.lineTo(-0.2915, 0.39394)
loop_1 = loop_1.lineTo(-0.27177, 0.35901)
loop_1 = loop_1.lineTo(-0.27204, 0.31762)
loop_1 = loop_1.lineTo(-0.29201, 0.29906)
loop_1 = loop_1.lineTo(-0.33467, 0.30088)
loop_1 = loop_1.lineTo(-0.37646, 0.30831)
loop_1 = loop_1.lineTo(-0.41739, 0.32119)
loop_1 = loop_1.lineTo(-0.45936, 0.34713)
loop_1 = loop_1.lineTo(-0.47367, 0.35968)
loop_1 = loop_1.lineTo(-0.458, 0.39191)
loop_1 = loop_1.lineTo(-0.41514, 0.39767)
loop_1 = loop_1.threePointArc((-0.37507, 0.39803), (-0.3335, 0.39803))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.35)

result = solid_1