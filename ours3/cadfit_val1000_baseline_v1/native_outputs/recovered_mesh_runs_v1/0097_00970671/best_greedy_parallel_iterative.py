import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.09, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02, 1.0)
loop_1 = loop_1.lineTo(-0.02, 1.0)
loop_1 = loop_1.lineTo(-0.01467, -1.0)
loop_1 = loop_1.lineTo(0.02, -1.0)
loop_1 = loop_1.lineTo(0.02, 0.99864)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
