import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.878, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.37753, 109.27439)
sketch_1 = sketch_1.circle(109.78997)
sketch_1 = sketch_1.moveTo(0.1416, 13.16947)
sketch_1 = sketch_1.circle(13.68507)
sketch_1 = sketch_1.moveTo(0.48507, 0.11072)
sketch_1 = sketch_1.circle(0.6263)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.084, -0.514, 0.879), axisEnd=(-0.916, -0.514, 0.879))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_7_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_7_revolve_1_ortho.stl')