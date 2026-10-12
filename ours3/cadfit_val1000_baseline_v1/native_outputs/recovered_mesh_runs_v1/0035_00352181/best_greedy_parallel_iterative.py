import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.33943, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.75999, 0.39122)
loop_1 = loop_1.lineTo(0.99886, 0.15007)
loop_1 = loop_1.lineTo(0.45529, -0.38893)
loop_1 = loop_1.lineTo(0.33643, -0.27236)
loop_1 = loop_1.lineTo(0.21595, -0.39122)
loop_1 = loop_1.lineTo(-1.0, -0.38799)
loop_1 = loop_1.lineTo(-0.99838, -0.2215)
loop_1 = loop_1.lineTo(0.15069, -0.21807)
loop_1 = loop_1.lineTo(0.75885, 0.39008)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.68)

result = solid_1
