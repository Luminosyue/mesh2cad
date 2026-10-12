import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.20751, -0.04743, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.55257, 1.20751)
loop_1 = loop_1.lineTo(-0.55257, -0.79249)
loop_1 = loop_1.lineTo(0.64743, -0.79249)
loop_1 = loop_1.lineTo(0.64743, 1.20751)
loop_1 = loop_1.lineTo(-0.52095, 1.20751)
loop_1 = loop_1.lineTo(-0.55257, 1.20751)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.35257, 1.00751)
loop_2 = loop_2.lineTo(0.44743, 1.00751)
loop_2 = loop_2.lineTo(0.44743, -0.59249)
loop_2 = loop_2.lineTo(-0.35257, -0.59249)
loop_2 = loop_2.lineTo(-0.35257, 0.98751)
loop_2 = loop_2.lineTo(-0.35257, 1.00751)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
