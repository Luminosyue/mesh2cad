import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.04689, -0.28429, -0.104), normal=(0.0, 1.0, 0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.04689, 0.61028)
loop_1 = loop_1.lineTo(-1.04689, -0.24686)
loop_1 = loop_1.lineTo(-0.47546, -0.24686)
loop_1 = loop_1.lineTo(-0.47546, -0.81829)
loop_1 = loop_1.lineTo(0.38168, -0.81829)
loop_1 = loop_1.lineTo(0.95311, -0.24686)
loop_1 = loop_1.lineTo(0.95311, 0.61028)
loop_1 = loop_1.lineTo(-1.0143, 0.61028)
loop_1 = loop_1.lineTo(-1.04689, 0.61028)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.57)

result = solid_1
