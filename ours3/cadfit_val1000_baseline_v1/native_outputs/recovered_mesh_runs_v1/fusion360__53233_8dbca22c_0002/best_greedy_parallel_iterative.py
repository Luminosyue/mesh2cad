import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01082, 0.00047, -0.08663), normal=(-0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02131, 0.98887)
loop_1 = loop_1.lineTo(-0.01935, -1.01052)
loop_1 = loop_1.lineTo(0.02038, -1.01052)
loop_1 = loop_1.lineTo(0.01803, 0.98887)
loop_1 = loop_1.lineTo(-0.02105, 0.98887)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
