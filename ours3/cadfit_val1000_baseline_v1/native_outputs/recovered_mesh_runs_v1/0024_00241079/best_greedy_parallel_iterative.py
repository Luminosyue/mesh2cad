import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.41947, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.0, 0.02632)
loop_1 = loop_1.lineTo(1.0, -0.02632)
loop_1 = loop_1.lineTo(-1.0, -0.02105)
loop_1 = loop_1.lineTo(-1.0, 0.02632)
loop_1 = loop_1.lineTo(0.99863, 0.02632)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.84)

result = solid_1
