import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.762, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.61035, 0.13247)
sketch_1 = sketch_1.circle(0.00222)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.612, 0.136, 0.763), axisEnd=(0.612, 1.136, 0.763))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_7_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_7_revolve_1_ortho.stl')