import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.75, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.3036)
loop_1 = loop_1.lineTo(1.0, 0.29891)
loop_1 = loop_1.lineTo(0.997, -0.30269)
loop_1 = loop_1.lineTo(-0.9985, 0.30315)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.5)

result = solid_1
