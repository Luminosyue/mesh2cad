import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.84692, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01769, 1.0)
loop_1 = loop_1.lineTo(-0.01769, 1.0)
loop_1 = loop_1.lineTo(-0.01238, -1.0)
loop_1 = loop_1.lineTo(0.01769, -1.0)
loop_1 = loop_1.lineTo(0.01769, 0.99864)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.69)

result = solid_1
