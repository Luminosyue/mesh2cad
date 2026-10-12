import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.22464), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.82339, -0.29016)
loop_1 = loop_1.lineTo(-0.40279, -0.99997)
loop_1 = loop_1.lineTo(0.41894, -0.99065)
loop_1 = loop_1.lineTo(0.82173, -0.27435)
loop_1 = loop_1.lineTo(0.40279, 0.43262)
loop_1 = loop_1.lineTo(-0.41894, 0.4233)
loop_1 = loop_1.lineTo(-0.82258, -0.28873)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.32)
plane_2 = cq.Plane(origin=(-0.48804, 0.05857, 0.09464), normal=(0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.05856, -0.12986)
loop_1 = loop_1.circle(0.64178)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.13)

result = solid_1
result = result.add(solid_2)