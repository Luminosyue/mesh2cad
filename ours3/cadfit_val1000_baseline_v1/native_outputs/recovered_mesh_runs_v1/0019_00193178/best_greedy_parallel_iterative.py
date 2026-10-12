import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.74266), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.89603, 0.94802)
loop_1 = loop_1.lineTo(-0.89094, -0.94292)
loop_1 = loop_1.lineTo(-0.58003, -0.62961)
loop_1 = loop_1.lineTo(-0.57522, 0.63201)
loop_1 = loop_1.lineTo(0.68739, 0.63541)
loop_1 = loop_1.lineTo(0.99759, 0.94802)
loop_1 = loop_1.lineTo(-0.89363, 0.94802)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.48)

result = solid_1
