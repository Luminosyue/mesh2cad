import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.24101, -0.01386, -0.31492), normal=(6e-05, 6e-05, 1.0), xDir=(0.0, 1.0, -6e-05))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.74829, 0.22325)
loop_1 = loop_1.lineTo(0.74906, 0.20322)
loop_1 = loop_1.lineTo(0.76408, 0.16206)
loop_1 = loop_1.lineTo(0.78306, 0.15205)
loop_1 = loop_1.lineTo(0.80104, 0.19591)
loop_1 = loop_1.lineTo(0.81324, 0.27147)
loop_1 = loop_1.lineTo(0.81308, 0.28224)
loop_1 = loop_1.lineTo(0.79005, 0.33893)
loop_1 = loop_1.lineTo(0.76139, 0.28884)
loop_1 = loop_1.lineTo(0.74604, 0.29558)
loop_1 = loop_1.lineTo(0.74306, 0.28014)
loop_1 = loop_1.lineTo(0.74808, 0.22552)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.57)

result = solid_1