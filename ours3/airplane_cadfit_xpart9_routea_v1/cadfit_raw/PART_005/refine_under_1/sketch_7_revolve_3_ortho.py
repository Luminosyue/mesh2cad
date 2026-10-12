import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 1.0, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.10448, 0.00069)
sketch_1 = sketch_1.circle(0.1123)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.105, 0.114, 1.001), axisEnd=(0.103, 1.1139999999999999, 1.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_7_revolve_3_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_7_revolve_3_ortho.stl')