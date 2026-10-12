import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.33315, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.25333)
loop_1 = loop_1.lineTo(-0.99851, 0.0751)
loop_1 = loop_1.lineTo(0.44658, 0.07073)
loop_1 = loop_1.lineTo(0.89747, -0.2509)
loop_1 = loop_1.lineTo(0.99879, -0.10792)
loop_1 = loop_1.lineTo(0.49363, 0.25333)
loop_1 = loop_1.lineTo(-0.99851, 0.25333)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.67)

result = solid_1
