import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.64647, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05882, 1.0)
loop_1 = loop_1.lineTo(0.05882, 0.99859)
loop_1 = loop_1.lineTo(0.05455, -1.0)
loop_1 = loop_1.lineTo(-0.05882, -0.99859)
loop_1 = loop_1.lineTo(-0.05882, 0.99859)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.29)

result = solid_1