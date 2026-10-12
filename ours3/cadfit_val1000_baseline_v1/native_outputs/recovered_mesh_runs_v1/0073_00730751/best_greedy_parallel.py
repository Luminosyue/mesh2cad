import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01899, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0146, 1.0)
loop_1 = loop_1.lineTo(0.00904, -1.0)
loop_1 = loop_1.lineTo(-0.0146, -1.0)
loop_1 = loop_1.lineTo(-0.00903, 1.0)
loop_1 = loop_1.lineTo(0.01321, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

# Revolve operation 1
plane_1 = cq.Plane(origin=(-0.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(1e-05, 1.0)
sketch_1 = sketch_1.lineTo(-0.01752, 1.0)
sketch_1 = sketch_1.lineTo(-0.01305, -1.0)
sketch_1 = sketch_1.lineTo(1e-05, -1.0)
sketch_1 = sketch_1.lineTo(1e-05, 1.0)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.001, 0.001, 0.001), axisEnd=(0.001, 1.001, 0.001))

result = solid_1
result = result.add(solid_revolve_1)