import cadquery as cq
import math

# Plane definition from JSON
origin = (1.0, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.51054, 0.0702)
sketch_1 = sketch_1.circle(2e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.509, 0.07100000000000001, 1.001), axisEnd=(-0.503, 1.071, 1.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/sketch_2_revolve_2_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/sketch_2_revolve_2_ortho.stl')