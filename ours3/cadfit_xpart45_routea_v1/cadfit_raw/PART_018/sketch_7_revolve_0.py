import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 1.0, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.05839, -0.16733)
sketch_1 = sketch_1.circle(9e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.057999999999999996, -0.166, 1.001), axisEnd=(-0.016999999999999998, -1.1660000000000001, 1.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_018/sketch_7_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_018/sketch_7_revolve_0.stl')