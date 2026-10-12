import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.626)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.94716, -7.94472)
sketch_1 = sketch_1.circle(7.91614)
sketch_1 = sketch_1.moveTo(-0.64662, -0.33698)
sketch_1 = sketch_1.circle(0.30841)
sketch_1 = sketch_1.moveTo(-0.56506, -1.61762)
sketch_1 = sketch_1.circle(1.58904)
sketch_1 = sketch_1.moveTo(0.87862, -0.71607)
sketch_1 = sketch_1.circle(0.68749)
sketch_1 = sketch_1.moveTo(0.94963, -1.9722)
sketch_1 = sketch_1.circle(1.94363)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.065, -0.028, 0.627), axisEnd=(0.935, -0.028, 0.627))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_11_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_11_revolve_1_ortho.stl')