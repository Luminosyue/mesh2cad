import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04718, 0.13662, 0.36463), normal=(-0.0, 0.0, -1.0), xDir=(0.0, -1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.13662, 0.82456)
loop_1 = loop_1.lineTo(1.13662, 0.11952)
loop_1 = loop_1.lineTo(0.39087, 0.11952)
loop_1 = loop_1.lineTo(0.39087, 0.82456)
loop_1 = loop_1.lineTo(1.12386, 0.82456)
loop_1 = loop_1.lineTo(1.13662, 0.82456)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.73)
plane_2 = cq.Plane(origin=(-0.04718, 0.13662, 0.36463), normal=(-0.0, 0.0, -1.0), xDir=(0.0, -1.0, -0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.46486, -0.52028)
loop_1 = loop_1.circle(0.39859)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.73)

result = solid_1
result = result.add(solid_2)