import cadquery as cq
import math

# Plane definition from JSON
origin = (0.846, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.02005, 0.00321)
sketch_1 = sketch_1.circle(0.01852)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.038, 0.004, 0.847), axisEnd=(-0.045, 1.0039999999999998, 0.847))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/sketch_3_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/sketch_3_revolve_3.stl')