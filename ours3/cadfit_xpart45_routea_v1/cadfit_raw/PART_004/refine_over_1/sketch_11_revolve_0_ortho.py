import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.996)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.02942, 1839.46082)
sketch_1 = sketch_1.circle(1839.09868)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.028999999999999998, 0.363, 0.997), axisEnd=(-1.0290000000000001, 0.363, 0.997))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_11_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_11_revolve_0_ortho.stl')