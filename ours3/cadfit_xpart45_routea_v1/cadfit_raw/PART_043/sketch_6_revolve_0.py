import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.722, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.94108, 0.5972)
sketch_1 = sketch_1.circle(1e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.942, 0.598, 0.723), axisEnd=(1.942, 0.587, 0.723))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/sketch_6_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/sketch_6_revolve_0.stl')