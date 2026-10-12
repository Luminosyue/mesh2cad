import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.91091, 0.01085, 0.0189), normal=(1.0, 0.0, -0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.01085, 0.92799)
loop_1 = loop_1.lineTo(1.01085, -0.89019)
loop_1 = loop_1.lineTo(-0.98915, -0.89019)
loop_1 = loop_1.lineTo(-0.98915, 0.92799)
loop_1 = loop_1.lineTo(0.01085, 0.92799)
loop_1 = loop_1.lineTo(0.01313, -0.16292)
loop_1 = loop_1.lineTo(0.19267, -0.16292)
loop_1 = loop_1.lineTo(0.19267, 0.92799)
loop_1 = loop_1.lineTo(0.99871, 0.92799)
loop_1 = loop_1.lineTo(1.01085, 0.92799)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.82)

result = solid_1
