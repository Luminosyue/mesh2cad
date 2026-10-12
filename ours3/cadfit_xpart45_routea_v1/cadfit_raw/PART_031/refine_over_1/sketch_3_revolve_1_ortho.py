import cadquery as cq
import math

# Plane definition from JSON
origin = (0.949, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(20.83133, 0.49327)
sketch_1 = sketch_1.circle(20.70566)
sketch_1 = sketch_1.moveTo(1015.64491, -0.127)
sketch_1 = sketch_1.circle(1015.51924)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.127, 0.184, 0.95), axisEnd=(0.127, 1.184, 0.95))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_3_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_3_revolve_1_ortho.stl')