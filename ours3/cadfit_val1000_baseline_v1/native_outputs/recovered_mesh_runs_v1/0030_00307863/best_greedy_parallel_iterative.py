import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.25), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.625, 1.0)
loop_1 = loop_1.lineTo(-0.62067, -1.0)
loop_1 = loop_1.lineTo(0.625, -0.99567)
loop_1 = loop_1.lineTo(0.62067, 1.0)
loop_1 = loop_1.lineTo(-0.62283, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
