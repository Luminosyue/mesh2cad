import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.308)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.79861, -0.22171)
sketch_1 = sketch_1.circle(1e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.8, -0.221, 0.309), axisEnd=(1.7999999999999998, -0.226, 0.309))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_11_revolve_1.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_11_revolve_1.stl')