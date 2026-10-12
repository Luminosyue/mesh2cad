import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.037, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.84118, 0.32169)
sketch_1 = sketch_1.lineTo(0.84112, 0.30835)
sketch_1 = sketch_1.lineTo(0.82979, 0.31339)
sketch_1 = sketch_1.threePointArc((0.77065, 0.31467), (0.71474, 0.31347))
sketch_1 = sketch_1.lineTo(0.40844, 0.31223)
sketch_1 = sketch_1.threePointArc((0.34178, 0.31246), (0.27865, 0.31171))
sketch_1 = sketch_1.lineTo(0.1605, 0.31214)
sketch_1 = sketch_1.threePointArc((0.0506, 0.31221), (-0.06298, 0.31293))
sketch_1 = sketch_1.threePointArc((-0.13138, 0.31288), (-0.19622, 0.31248))
sketch_1 = sketch_1.threePointArc((0.31102, 0.31805), (0.8403, 0.32165))
sketch_1 = sketch_1.close()
sketch_1 = sketch_1.moveTo(-0.81842, 0.30776)
sketch_1 = sketch_1.lineTo(-0.83161, 0.30251)
sketch_1 = sketch_1.lineTo(-0.81842, 0.30776)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.31, 0.313, -0.036), axisEnd=(-1.31, 0.304, -0.036))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_0_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_0_revolve_0_ortho.stl')