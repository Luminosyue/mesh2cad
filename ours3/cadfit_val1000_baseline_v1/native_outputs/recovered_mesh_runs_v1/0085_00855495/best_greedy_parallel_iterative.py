import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.06, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.01)
loop_1 = loop_1.lineTo(1.0, 0.00571)
loop_1 = loop_1.lineTo(1.0, -0.01)
loop_1 = loop_1.lineTo(-1.0, -0.00571)
loop_1 = loop_1.lineTo(-1.0, 0.00857)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

# Revolve operation 1
plane_1 = cq.Plane(origin=(0.0, -0.06, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(-1.0, 0.01)
sketch_1 = sketch_1.lineTo(1.0, 0.00571)
sketch_1 = sketch_1.lineTo(1.0, -0.01)
sketch_1 = sketch_1.lineTo(-1.0, -0.00571)
sketch_1 = sketch_1.lineTo(-1.0, 0.00857)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.001, 0.001, 0.001), axisEnd=(1.001, 0.001, 0.001))

result = solid_1
result = result.add(solid_revolve_1)