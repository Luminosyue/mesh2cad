import cadquery as cq
import math

# Plane definition from JSON
origin = (0.943, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.08339, 0.02968)
sketch_1 = sketch_1.circle(0.0001)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.084, 0.031, 0.944), axisEnd=(1.0839999999999999, 0.030000000000000002, 0.944))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_3_revolve_2.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_3_revolve_2.stl')