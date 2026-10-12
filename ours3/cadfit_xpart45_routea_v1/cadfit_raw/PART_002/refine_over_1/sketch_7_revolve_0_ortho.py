import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.408, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.12434, 111.84997)
sketch_1 = sketch_1.circle(111.99066)
sketch_1 = sketch_1.moveTo(0.17067, 57.18834)
sketch_1 = sketch_1.circle(57.32903)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.024, -0.13999999999999999, 0.409), axisEnd=(-0.976, -0.13999999999999999, 0.409))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_7_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_7_revolve_0_ortho.stl')