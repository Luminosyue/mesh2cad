import cadquery as cq
import math

# Plane definition from JSON
origin = (0.052, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.97849, 0.00434)
sketch_1 = sketch_1.circle(1e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.979, 0.005, 0.053), axisEnd=(1.9789999999999999, 0.0, 0.053))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_3_revolve_1.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_3_revolve_1.stl')