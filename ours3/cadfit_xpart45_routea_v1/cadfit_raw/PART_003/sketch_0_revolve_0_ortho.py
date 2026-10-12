import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.038, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.12226, -0.00397)
sketch_1 = sketch_1.lineTo(-0.19207, -0.01001)
sketch_1 = sketch_1.lineTo(-0.21028, -0.01186)
sketch_1 = sketch_1.lineTo(-0.27226, -0.01579)
sketch_1 = sketch_1.threePointArc((-0.31588, -0.01692), (-0.35715, -0.01874))
sketch_1 = sketch_1.threePointArc((-0.51644, -0.02205), (-0.68178, -0.0224))
sketch_1 = sketch_1.threePointArc((-0.80889, -0.02134), (-0.94065, -0.01855))
sketch_1 = sketch_1.threePointArc((-0.95909, -0.01851), (-0.97767, -0.01748))
sketch_1 = sketch_1.threePointArc((-0.99071, -0.00933), (-0.99458, -0.00384))
sketch_1 = sketch_1.lineTo(-0.12226, -0.00397)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.561, 0.0, -0.037), axisEnd=(-1.5610000000000002, 0.0, -0.037))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_003/sketch_0_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_003/sketch_0_revolve_0_ortho.stl')