import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.01042, -0.00147), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.78964, 0.04398)
loop_1 = loop_1.lineTo(0.78964, -0.04693)
loop_1 = loop_1.lineTo(-0.7688, -0.0455)
loop_1 = loop_1.lineTo(-0.7688, 0.04398)
loop_1 = loop_1.lineTo(0.78434, 0.04398)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
