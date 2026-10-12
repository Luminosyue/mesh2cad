import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.25, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.625)
loop_1 = loop_1.lineTo(-0.99567, -0.625)
loop_1 = loop_1.lineTo(1.0, -0.62067)
loop_1 = loop_1.lineTo(0.99567, 0.625)
loop_1 = loop_1.lineTo(-0.99783, 0.625)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
