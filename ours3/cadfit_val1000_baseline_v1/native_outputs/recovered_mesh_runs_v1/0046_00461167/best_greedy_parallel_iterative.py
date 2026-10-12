import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.35109), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.0)
loop_1 = loop_1.lineTo(-0.496, -0.86603)
loop_1 = loop_1.lineTo(0.502, -0.86256)
loop_1 = loop_1.lineTo(0.998, 0.00346)
loop_1 = loop_1.lineTo(0.496, 0.86603)
loop_1 = loop_1.lineTo(-0.502, 0.86256)
loop_1 = loop_1.lineTo(-0.999, 0.00173)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.7)

result = solid_1
