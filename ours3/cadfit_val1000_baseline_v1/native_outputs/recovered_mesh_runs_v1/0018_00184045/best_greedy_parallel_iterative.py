import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00518, 1.0, 0.03631), normal=(0.0, -1.0, 0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28053, 0.32202)
loop_1 = loop_1.lineTo(-0.29089, 0.32202)
loop_1 = loop_1.lineTo(-0.29089, -0.2494)
loop_1 = loop_1.lineTo(0.28053, -0.2494)
loop_1 = loop_1.lineTo(0.28053, 0.31065)
loop_1 = loop_1.lineTo(0.28053, 0.32202)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.20911, 0.2506)
loop_2 = loop_2.lineTo(0.20911, -0.17798)
loop_2 = loop_2.lineTo(-0.21947, -0.17798)
loop_2 = loop_2.lineTo(-0.21947, 0.2506)
loop_2 = loop_2.lineTo(0.19839, 0.2506)
loop_2 = loop_2.lineTo(0.20911, 0.2506)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
