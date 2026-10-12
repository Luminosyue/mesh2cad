import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.50747, -0.08428, -0.1651), normal=(0.0, -1.0, 0.0), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.49253, 0.59657)
loop_1 = loop_1.lineTo(0.49253, 0.25805)
loop_1 = loop_1.lineTo(0.15401, 0.25805)
loop_1 = loop_1.lineTo(0.15401, 0.59657)
loop_1 = loop_1.lineTo(0.48539, 0.59657)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.34)
plane_2 = cq.Plane(origin=(-0.50747, -0.08428, -0.1651), normal=(0.0, -1.0, 0.0), xDir=(-1.0, -0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.42949, -0.55543)
loop_1 = loop_1.circle(0.16885)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.34)

result = solid_1
result = result.add(solid_2)