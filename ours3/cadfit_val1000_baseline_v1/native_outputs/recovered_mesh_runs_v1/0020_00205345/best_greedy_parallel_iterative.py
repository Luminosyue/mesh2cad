import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00612, 0.31231, 0.13347), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.3785, 0.78732)
loop_1 = loop_1.lineTo(0.3785, -0.21269)
loop_1 = loop_1.lineTo(0.99388, -0.21269)
loop_1 = loop_1.lineTo(0.99388, -0.52038)
loop_1 = loop_1.lineTo(-1.00612, -0.52038)
loop_1 = loop_1.lineTo(-1.00612, -0.21269)
loop_1 = loop_1.lineTo(-0.39073, -0.21269)
loop_1 = loop_1.lineTo(-0.39073, 0.78732)
loop_1 = loop_1.lineTo(0.34725, 0.78732)
loop_1 = loop_1.lineTo(0.3785, 0.78732)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.00612, 0.55655)
loop_2 = loop_2.circle(0.11544)
loop_3 = sketch_1.moveTo(-0.00612, -0.28961)
loop_3 = loop_3.circle(0.07595)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3)
solid_1 = sketch_1.extrude(0.62)

result = solid_1
