import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.06642, 0.12445, 0.99867), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.29111, 0.23309)
loop_1 = loop_1.lineTo(0.29111, -0.10025)
loop_1 = loop_1.lineTo(-0.04222, -0.10025)
loop_1 = loop_1.lineTo(-0.04222, 0.23309)
loop_1 = loop_1.lineTo(0.28463, 0.23309)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
