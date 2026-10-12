import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.993, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(115.25062, 0.38643)
sketch_1 = sketch_1.circle(115.25327)
sketch_1 = sketch_1.moveTo(171.73638, 0.02388)
sketch_1 = sketch_1.circle(171.73903)
sketch_1 = sketch_1.moveTo(5.39991, -0.50415)
sketch_1 = sketch_1.circle(5.40255)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.002, -0.03, 0.994), axisEnd=(-0.002, 0.97, 0.994))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_7_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_7_revolve_0_ortho.stl')