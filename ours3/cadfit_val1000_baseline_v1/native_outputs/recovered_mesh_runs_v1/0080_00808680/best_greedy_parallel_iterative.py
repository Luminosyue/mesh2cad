import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02809, 0.5, -0.01401), normal=(0.0, -1.0, 0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.97191, 0.31932)
loop_1 = loop_1.lineTo(0.97191, -0.34734)
loop_1 = loop_1.lineTo(-0.36142, -0.34734)
loop_1 = loop_1.lineTo(-0.36142, -0.01401)
loop_1 = loop_1.lineTo(-0.69475, -0.01401)
loop_1 = loop_1.lineTo(-0.69475, -0.34734)
loop_1 = loop_1.lineTo(-1.02809, -0.34734)
loop_1 = loop_1.lineTo(-1.02809, 0.31932)
loop_1 = loop_1.lineTo(0.96566, 0.31932)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.0)

result = solid_1
