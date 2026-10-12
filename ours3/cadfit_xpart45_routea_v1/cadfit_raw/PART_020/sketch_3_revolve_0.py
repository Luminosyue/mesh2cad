import cadquery as cq
import math

# Plane definition from JSON
origin = (0.92, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.04052, 0.2156)
sketch_1 = sketch_1.circle(3e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.04, 0.217, 0.921), axisEnd=(0.96, 0.199, 0.921))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_020/sketch_3_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_020/sketch_3_revolve_0.stl')