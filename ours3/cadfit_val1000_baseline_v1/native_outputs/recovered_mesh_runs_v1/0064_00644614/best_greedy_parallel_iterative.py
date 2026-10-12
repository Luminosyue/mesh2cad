import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.38955, 0.50646)
loop_1 = loop_1.lineTo(-0.38745, -0.10129)
loop_1 = loop_1.lineTo(-0.38406, -0.50646)
loop_1 = loop_1.lineTo(0.38729, -0.50407)
loop_1 = loop_1.lineTo(0.3884, -0.10129)
loop_1 = loop_1.lineTo(0.38729, 0.50646)
loop_1 = loop_1.lineTo(-0.3885, 0.50646)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
