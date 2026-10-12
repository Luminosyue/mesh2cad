import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.368, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-64.76793, -0.04257)
sketch_1 = sketch_1.circle(64.16246)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.605, -0.041999999999999996, -0.367), axisEnd=(-0.605, -1.042, -0.367))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_3_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_3_revolve_3.stl')