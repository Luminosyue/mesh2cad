import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.996)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(532.54875, 0.12516)
sketch_1 = sketch_1.circle(532.86151)
sketch_1 = sketch_1.moveTo(52.69531, -0.22141)
sketch_1 = sketch_1.circle(53.00807)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.312, -0.047, 0.997), axisEnd=(-0.312, 0.953, 0.997))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_11_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_11_revolve_1_ortho.stl')