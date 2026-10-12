import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.5, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-4.47837, 0.10167)
sketch_1 = sketch_1.circle(3.84879)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.629, 0.041, 0.501), axisEnd=(-0.62, 1.041, 0.501))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_6_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_6_revolve_1_ortho.stl')