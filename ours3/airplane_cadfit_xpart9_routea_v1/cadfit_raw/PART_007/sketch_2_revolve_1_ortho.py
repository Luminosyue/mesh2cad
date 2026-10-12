import cadquery as cq
import math

# Plane definition from JSON
origin = (1.0, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.51052, 0.07081)
sketch_1 = sketch_1.circle(0.00061)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.51, 0.07100000000000001, 1.001), axisEnd=(-1.5090000000000001, 0.06, 1.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/sketch_2_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/sketch_2_revolve_1_ortho.stl')