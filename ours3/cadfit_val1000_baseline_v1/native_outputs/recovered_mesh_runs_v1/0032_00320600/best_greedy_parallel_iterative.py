import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.3935, 0.29343)
loop_1 = loop_1.lineTo(-0.28627, -0.29124)
loop_1 = loop_1.lineTo(-0.39201, 0.24365)
loop_1 = loop_1.lineTo(0.39276, 0.29339)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
