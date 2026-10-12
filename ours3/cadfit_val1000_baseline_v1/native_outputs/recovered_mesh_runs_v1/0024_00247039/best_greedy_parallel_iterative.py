import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00362, -1.0, -0.13279), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.99638, 0.86721)
loop_1 = loop_1.lineTo(1.00362, 0.86721)
loop_1 = loop_1.lineTo(1.0005, -1.13279)
loop_1 = loop_1.lineTo(0.50362, -1.13279)
loop_1 = loop_1.lineTo(0.50362, -0.38279)
loop_1 = loop_1.lineTo(-0.49638, -0.38279)
loop_1 = loop_1.lineTo(-0.4995, -1.13279)
loop_1 = loop_1.lineTo(-0.99638, -1.13279)
loop_1 = loop_1.lineTo(-0.99638, 0.85784)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
