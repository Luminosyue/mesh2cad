import cadquery as cq
import math

# Plane definition from JSON
origin = (0.653, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(7958.05004, 0.21)
sketch_1 = sketch_1.circle(7957.08406)
sketch_1 = sketch_1.moveTo(3800.13683, -0.17493)
sketch_1 = sketch_1.circle(3799.17086)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.967, 0.019, 0.654), axisEnd=(0.967, 1.019, 0.654))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_3_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_3_revolve_1_ortho.stl')