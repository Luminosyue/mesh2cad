import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0485, -0.4, -0.06954), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.9515, 0.38046)
loop_1 = loop_1.lineTo(-0.9515, -0.21954)
loop_1 = loop_1.lineTo(-0.7515, -0.21954)
loop_1 = loop_1.lineTo(-0.7515, -0.51954)
loop_1 = loop_1.lineTo(0.0485, -0.51954)
loop_1 = loop_1.lineTo(0.0485, -0.21954)
loop_1 = loop_1.lineTo(1.0485, -0.21954)
loop_1 = loop_1.lineTo(1.0485, 0.38046)
loop_1 = loop_1.lineTo(-0.94108, 0.38046)
loop_1 = loop_1.lineTo(-0.9515, 0.38046)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.8)

result = solid_1
