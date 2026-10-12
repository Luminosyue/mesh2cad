import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.979, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.00738, -0.1641)
sketch_1 = sketch_1.circle(0.00021)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.007, -0.163, 0.98), axisEnd=(-0.028, 0.837, 0.98))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/sketch_7_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/sketch_7_revolve_0_ortho.stl')