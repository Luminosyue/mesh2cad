import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.365)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-41.46874, -0.43286)
sketch_1 = sketch_1.circle(41.58361)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.116, -0.432, 0.366), axisEnd=(0.116, -1.4320000000000002, 0.366))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_11_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_11_revolve_3.stl')