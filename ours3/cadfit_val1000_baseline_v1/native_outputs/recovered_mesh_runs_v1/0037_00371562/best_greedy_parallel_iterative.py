import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.36364, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.54545)
loop_1 = loop_1.lineTo(-0.99588, -0.54545)
loop_1 = loop_1.lineTo(-0.27273, -0.54339)
loop_1 = loop_1.lineTo(-0.27067, 0.18182)
loop_1 = loop_1.lineTo(1.0, 0.18595)
loop_1 = loop_1.lineTo(0.99794, 0.54545)
loop_1 = loop_1.lineTo(-0.99794, 0.54545)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.73)

result = solid_1
