import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.22923, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.70721, -1.0)
loop_1 = loop_1.lineTo(-0.88308, 0.5878)
loop_1 = loop_1.lineTo(-0.88087, 1.0)
loop_1 = loop_1.lineTo(0.88308, 0.9956)
loop_1 = loop_1.lineTo(0.87868, -1.0)
loop_1 = loop_1.lineTo(0.70941, -1.0)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.74761, 0.50959)
loop_2 = loop_2.threePointArc((-0.66572, 0.46442), (-0.58181, 0.41491))
loop_2 = loop_2.threePointArc((0.14964, -0.18497), (0.70439, -0.99559))
loop_2 = loop_2.lineTo(-0.88308, 0.58723)
loop_2 = loop_2.lineTo(-0.88032, 1.0)
loop_2 = loop_2.lineTo(0.86989, 0.99604)
loop_2 = loop_2.lineTo(-0.74468, 0.51093)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.46)

result = solid_1