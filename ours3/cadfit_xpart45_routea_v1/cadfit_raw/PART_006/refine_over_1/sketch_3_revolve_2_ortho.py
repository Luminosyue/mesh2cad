import cadquery as cq
import math

# Plane definition from JSON
origin = (0.997, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.29479, 45.16955)
sketch_1 = sketch_1.circle(44.97576)
sketch_1 = sketch_1.moveTo(-0.19532, 50.37765)
sketch_1 = sketch_1.circle(50.18386)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.051000000000000004, 0.195, 0.998), axisEnd=(-0.949, 0.195, 0.998))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_3_revolve_2_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_3_revolve_2_ortho.stl')