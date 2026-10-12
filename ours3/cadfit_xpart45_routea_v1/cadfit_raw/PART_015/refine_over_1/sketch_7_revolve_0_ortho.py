import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.999, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(9.81991, 0.20045)
sketch_1 = sketch_1.circle(9.88065)
sketch_1 = sketch_1.moveTo(1390.50689, -0.00686)
sketch_1 = sketch_1.circle(1390.56763)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.06, 0.098, 1.0), axisEnd=(-0.06, 1.0979999999999999, 1.0))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_7_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_7_revolve_0_ortho.stl')