import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.55319, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.36357, 0.57986)
loop_1 = loop_1.lineTo(0.3652, -0.19329)
loop_1 = loop_1.lineTo(0.78786, -0.19169)
loop_1 = loop_1.lineTo(0.78622, 0.57986)
loop_1 = loop_1.lineTo(0.36437, 0.57986)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.85)
plane_2 = cq.Plane(origin=(-0.62, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.29811, 0.19329)
loop_1 = loop_1.lineTo(-0.30016, -0.57986)
loop_1 = loop_1.lineTo(-0.55362, -0.5785)
loop_1 = loop_1.lineTo(-0.55157, 0.19329)
loop_1 = loop_1.lineTo(-0.29879, 0.19329)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.62)

result = solid_1
result = result.add(solid_2)