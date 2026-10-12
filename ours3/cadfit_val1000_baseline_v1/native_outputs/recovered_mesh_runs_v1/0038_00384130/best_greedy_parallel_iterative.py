import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.67, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.86667, 0.06667)
loop_1 = loop_1.lineTo(-0.24533, 0.06521)
loop_1 = loop_1.lineTo(-0.24582, -0.06667)
loop_1 = loop_1.lineTo(-0.73406, -0.06521)
loop_1 = loop_1.lineTo(-0.7345, 0.00022)
loop_1 = loop_1.lineTo(-0.86623, 0.06645)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.73406, -0.0)
loop_2 = loop_2.lineTo(-0.86521, 0.06667)
loop_2 = loop_2.lineTo(-0.24533, 0.06521)
loop_2 = loop_2.lineTo(-0.24584, -0.06667)
loop_2 = loop_2.lineTo(-0.73406, -0.06521)
loop_2 = loop_2.lineTo(-0.73406, -0.00049)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(1.34)

result = solid_1