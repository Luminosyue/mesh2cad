import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.037, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.84033, 0.30873)
sketch_1 = sketch_1.lineTo(0.82979, 0.31339)
sketch_1 = sketch_1.threePointArc((0.77201, 0.31467), (0.71739, 0.31353))
sketch_1 = sketch_1.threePointArc((0.64562, 0.31378), (0.57758, 0.31301))
sketch_1 = sketch_1.lineTo(0.36263, 0.3124)
sketch_1 = sketch_1.lineTo(0.27523, 0.31211)
sketch_1 = sketch_1.lineTo(0.16306, 0.31211)
sketch_1 = sketch_1.lineTo(-0.02968, 0.31277)
sketch_1 = sketch_1.threePointArc((-0.07422, 0.31254), (-0.11972, 0.3128))
sketch_1 = sketch_1.lineTo(0.84033, 0.30873)
sketch_1 = sketch_1.close()
sketch_1 = sketch_1.moveTo(-0.81913, 0.30744)
sketch_1 = sketch_1.lineTo(-0.83161, 0.30253)
sketch_1 = sketch_1.lineTo(-0.81913, 0.30744)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.31, 0.313, -0.036), axisEnd=(-1.31, 0.31, -0.036))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_0_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_0_revolve_1_ortho.stl')