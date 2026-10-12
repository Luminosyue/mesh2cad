import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00991, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.55997, 0.40597)
loop_1 = loop_1.lineTo(0.03378, 0.40398)
loop_1 = loop_1.lineTo(0.035, 0.2222)
loop_1 = loop_1.lineTo(0.48504, 0.2202)
loop_1 = loop_1.lineTo(0.48592, 0.03654)
loop_1 = loop_1.lineTo(0.81155, 0.03552)
loop_1 = loop_1.lineTo(0.81243, -0.15102)
loop_1 = loop_1.lineTo(0.9741, -0.15001)
loop_1 = loop_1.lineTo(0.97349, 0.03654)
loop_1 = loop_1.lineTo(0.86137, 0.03755)
loop_1 = loop_1.lineTo(0.86055, 0.2241)
loop_1 = loop_1.lineTo(0.55997, 0.22508)
loop_1 = loop_1.lineTo(0.55997, 0.40497)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
