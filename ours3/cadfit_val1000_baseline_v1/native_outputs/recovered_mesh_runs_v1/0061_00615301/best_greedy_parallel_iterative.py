import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01272, -0.56659, -0.15585), normal=(0.0, 1.0, 0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.01272, 0.49177)
loop_1 = loop_1.lineTo(0.98728, 0.48853)
loop_1 = loop_1.lineTo(0.98638, -0.80347)
loop_1 = loop_1.lineTo(0.62918, -0.80097)
loop_1 = loop_1.lineTo(0.62594, 0.19462)
loop_1 = loop_1.lineTo(-0.66605, 0.19213)
loop_1 = loop_1.lineTo(-0.66692, -0.80347)
loop_1 = loop_1.lineTo(-1.01272, -0.80347)
loop_1 = loop_1.lineTo(-1.01272, 0.48327)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.13)

result = solid_1
