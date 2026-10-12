import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.21495, 0.00935)
loop_1 = loop_1.lineTo(0.21495, 0.00815)
loop_1 = loop_1.lineTo(0.21465, -0.00935)
loop_1 = loop_1.lineTo(-0.21495, -0.00815)
loop_1 = loop_1.lineTo(-0.21495, 0.00905)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)
plane_2 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.21495, 0.00935)
loop_1 = loop_1.lineTo(0.21495, 0.00844)
loop_1 = loop_1.lineTo(0.21465, -0.00935)
loop_1 = loop_1.lineTo(-0.21495, -0.00844)
loop_1 = loop_1.lineTo(-0.21495, 0.00904)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(2.0)

result = solid_1
result = result.add(solid_2)