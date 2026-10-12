import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.26838, 0.39594)
loop_1 = loop_1.lineTo(-0.26838, 0.39417)
loop_1 = loop_1.lineTo(-0.2666, -0.39594)
loop_1 = loop_1.lineTo(0.26838, -0.39417)
loop_1 = loop_1.lineTo(0.26838, 0.39505)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
