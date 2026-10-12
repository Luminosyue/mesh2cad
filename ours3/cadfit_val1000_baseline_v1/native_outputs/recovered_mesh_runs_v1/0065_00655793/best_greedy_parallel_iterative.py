import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00315, -1.0, 0.00492), normal=(-0.0, 1.0, -0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04796, 0.27579)
loop_1 = loop_1.lineTo(0.04166, 0.27579)
loop_1 = loop_1.lineTo(0.04166, -0.26595)
loop_1 = loop_1.lineTo(-0.00722, -0.26595)
loop_1 = loop_1.lineTo(-0.00722, -0.23376)
loop_1 = loop_1.lineTo(-0.04796, -0.23376)
loop_1 = loop_1.lineTo(-0.04796, 0.18172)
loop_1 = loop_1.lineTo(-0.00722, 0.18172)
loop_1 = loop_1.lineTo(-0.00722, 0.2143)
loop_1 = loop_1.lineTo(-0.04796, 0.2143)
loop_1 = loop_1.lineTo(-0.04796, 0.27425)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
