import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.29421, 0.73096, -0.01517), normal=(0.0, -1.0, 0.0), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.70579, 0.02341)
loop_1 = loop_1.lineTo(0.70579, -0.01547)
loop_1 = loop_1.lineTo(-0.09724, -0.01547)
loop_1 = loop_1.lineTo(-0.49876, -0.02503)
loop_1 = loop_1.lineTo(-1.25463, 0.00397)
loop_1 = loop_1.lineTo(-0.09724, 0.00397)
loop_1 = loop_1.lineTo(-0.09724, 0.02341)
loop_1 = loop_1.lineTo(0.68744, 0.02341)
loop_1 = loop_1.lineTo(0.70579, 0.02341)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.46)

result = solid_1