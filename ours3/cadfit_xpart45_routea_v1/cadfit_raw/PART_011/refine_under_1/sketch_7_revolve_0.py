import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 1.0, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.07722, -0.04932)
sketch_1 = sketch_1.circle(4e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.078, -0.048, 1.001), axisEnd=(0.052, 0.951, 1.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_7_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_7_revolve_0.stl')