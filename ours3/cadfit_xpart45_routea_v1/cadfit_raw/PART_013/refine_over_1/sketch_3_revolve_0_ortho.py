import cadquery as cq
import math

# Plane definition from JSON
origin = (0.884, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(3.25023, 0.12558)
sketch_1 = sketch_1.circle(3.16608)
sketch_1 = sketch_1.moveTo(1.7125, -0.11445)
sketch_1 = sketch_1.circle(1.62835)
sketch_1 = sketch_1.moveTo(0.31991, -0.23061)
sketch_1 = sketch_1.circle(0.23576)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.085, -0.072, 0.885), axisEnd=(0.085, 0.928, 0.885))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_3_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_3_revolve_0_ortho.stl')