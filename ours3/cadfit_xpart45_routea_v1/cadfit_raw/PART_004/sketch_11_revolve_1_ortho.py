import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 1.0)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.2763, 0.36067)
sketch_1 = sketch_1.circle(0.0001)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.275, 0.362, 1.001), axisEnd=(-1.2750000000000001, 0.34, 1.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/sketch_11_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/sketch_11_revolve_1_ortho.stl')