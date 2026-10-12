import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00548, -0.02919, -0.00112), normal=(0.0, 0.99913, 0.0417), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.00548, 0.01491)
loop_1 = loop_1.lineTo(-1.00548, -0.01625)
loop_1 = loop_1.lineTo(0.99452, -0.0143)
loop_1 = loop_1.lineTo(0.99452, 0.01491)
loop_1 = loop_1.lineTo(-1.0051, 0.01491)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
