import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.486, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.19849, -0.02624)
sketch_1 = sketch_1.circle(1e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.199, -0.024999999999999998, 0.487), axisEnd=(1.1989999999999998, -0.02, 0.487))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_012/sketch_7_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_012/sketch_7_revolve_0.stl')