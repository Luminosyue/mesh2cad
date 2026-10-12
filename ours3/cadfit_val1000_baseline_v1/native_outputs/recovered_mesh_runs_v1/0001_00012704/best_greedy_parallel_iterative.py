import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.32622, 0.17445, -0.90635), normal=(0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.9681, 0.67378)
loop_1 = loop_1.lineTo(-0.9681, -0.91352)
loop_1 = loop_1.lineTo(0.6192, -0.91352)
loop_1 = loop_1.lineTo(0.6192, 0.67378)
loop_1 = loop_1.lineTo(-0.93667, 0.67378)
loop_1 = loop_1.lineTo(-0.9681, 0.67378)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.7)

result = solid_1
