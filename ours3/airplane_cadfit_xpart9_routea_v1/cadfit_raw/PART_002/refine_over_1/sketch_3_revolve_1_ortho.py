import cadquery as cq
import math

# Plane definition from JSON
origin = (0.989, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(194.97198, -0.08304)
sketch_1 = sketch_1.circle(194.92905)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.044, -0.082, 0.99), axisEnd=(0.044, 0.918, 0.99))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_3_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_3_revolve_1_ortho.stl')