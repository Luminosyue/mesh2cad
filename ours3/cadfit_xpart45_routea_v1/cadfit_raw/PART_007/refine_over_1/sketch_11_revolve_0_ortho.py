import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.626)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.94689, 7.8194)
sketch_1 = sketch_1.circle(7.84823)
sketch_1 = sketch_1.moveTo(-0.64641, 0.26714)
sketch_1 = sketch_1.circle(0.29596)
sketch_1 = sketch_1.moveTo(-0.56513, 1.4779)
sketch_1 = sketch_1.circle(1.50672)
sketch_1 = sketch_1.moveTo(0.87857, 0.6087)
sketch_1 = sketch_1.circle(0.63753)
sketch_1 = sketch_1.moveTo(0.94954, 1.85798)
sketch_1 = sketch_1.circle(1.88682)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.065, -0.028, 0.627), axisEnd=(-1.0650000000000002, -0.028, 0.627))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_11_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_11_revolve_0_ortho.stl')