import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.899, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.51769, 0.11198)
sketch_1 = sketch_1.circle(1e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.517, 0.113, 0.9), axisEnd=(-0.537, 1.113, 0.9))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/sketch_6_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/sketch_6_revolve_0.stl')