import cadquery as cq
import math

# Plane definition from JSON
origin = (1.0, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.02217, -0.15843)
sketch_1 = sketch_1.circle(4e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.023, -0.157, 1.001), axisEnd=(0.013999999999999999, 0.843, 1.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/sketch_3_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/sketch_3_revolve_0_ortho.stl')