import cadquery as cq
import math

# Plane definition from JSON
origin = (0.994, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.13515, 0.87187)
sketch_1 = sketch_1.circle(0.69007)
sketch_1 = sketch_1.moveTo(0.04761, 19.93152)
sketch_1 = sketch_1.circle(19.74971)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.092, 0.183, 0.995), axisEnd=(-0.908, 0.183, 0.995))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_3_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_3_revolve_0_ortho.stl')