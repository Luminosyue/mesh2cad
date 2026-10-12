import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.82697, 0.96981)
loop_1 = loop_1.lineTo(0.13532, 0.11586)
loop_1 = loop_1.lineTo(0.13976, -0.96981)
loop_1 = loop_1.lineTo(0.82697, -0.96759)
loop_1 = loop_1.lineTo(0.82254, 0.96981)
loop_1 = loop_1.lineTo(-0.82475, 0.96981)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
