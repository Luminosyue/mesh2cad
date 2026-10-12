import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.978, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(561.51618, 0.18327)
sketch_1 = sketch_1.circle(561.53104)
sketch_1 = sketch_1.moveTo(88.84129, -0.40393)
sketch_1 = sketch_1.circle(88.85615)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.013999999999999999, -0.109, 0.979), axisEnd=(-0.013999999999999999, 0.891, 0.979))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_7_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_7_revolve_0_ortho.stl')