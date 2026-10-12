import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.35857), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.71786, 0.8)
loop_1 = loop_1.lineTo(-0.7143, -0.22857)
loop_1 = loop_1.lineTo(0.23929, -0.22503)
loop_1 = loop_1.lineTo(0.24106, 0.28571)
loop_1 = loop_1.lineTo(0.71786, 0.2875)
loop_1 = loop_1.lineTo(0.71786, 0.31428)
loop_1 = loop_1.lineTo(0.23929, 0.31606)
loop_1 = loop_1.lineTo(0.23751, 1.0)
loop_1 = loop_1.lineTo(-0.38214, 0.99821)
loop_1 = loop_1.lineTo(-0.38392, 0.8)
loop_1 = loop_1.lineTo(-0.71608, 0.8)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.29)

result = solid_1
