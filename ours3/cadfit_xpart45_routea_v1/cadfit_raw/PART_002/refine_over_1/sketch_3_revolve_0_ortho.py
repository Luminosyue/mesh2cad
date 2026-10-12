import cadquery as cq
import math

# Plane definition from JSON
origin = (0.615, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.16274, 733.47126)
sketch_1 = sketch_1.circle(732.75646)
sketch_1 = sketch_1.moveTo(-0.01006, 1.28653)
sketch_1 = sketch_1.circle(0.57176)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.077, 0.716, 0.616), axisEnd=(-0.923, 0.716, 0.616))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_3_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_3_revolve_0_ortho.stl')