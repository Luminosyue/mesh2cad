import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.304, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.10303, 0.00467)
sketch_1 = sketch_1.circle(2e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.104, 0.006, 0.305), axisEnd=(1.1039999999999999, 0.037, 0.305))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_7_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_7_revolve_1_ortho.stl')