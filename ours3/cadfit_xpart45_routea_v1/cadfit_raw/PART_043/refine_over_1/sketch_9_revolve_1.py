import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.62)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.3251, 0.61687)
sketch_1 = sketch_1.circle(0.0001)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.324, 0.618, 0.621), axisEnd=(0.64, 0.353, 0.621))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_9_revolve_1.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_9_revolve_1.stl')