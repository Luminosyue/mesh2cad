import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.0, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.55633, 0.03761)
sketch_1 = sketch_1.lineTo(-0.99198, 0.03484)
sketch_1 = sketch_1.lineTo(-0.99448, 0.0152)
sketch_1 = sketch_1.threePointArc((-0.98357, 0.01252), (-0.97279, 0.01297))
sketch_1 = sketch_1.threePointArc((-0.32587, 0.01241), (0.34663, 0.01083))
sketch_1 = sketch_1.lineTo(0.99482, 0.01392)
sketch_1 = sketch_1.lineTo(0.99914, 0.02494)
sketch_1 = sketch_1.lineTo(0.98798, 0.03535)
sketch_1 = sketch_1.lineTo(-0.09211, 0.0365)
sketch_1 = sketch_1.threePointArc((-0.32924, 0.03726), (-0.55509, 0.03737))
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.0, 0.001, 0.001), axisEnd=(1.0, 0.001, 0.001))
