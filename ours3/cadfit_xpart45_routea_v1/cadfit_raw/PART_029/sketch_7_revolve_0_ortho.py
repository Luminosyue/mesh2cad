import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.238, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.87258, 0.12854)
sketch_1 = sketch_1.circle(9e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.872, 0.13, 0.239), axisEnd=(-0.844, 1.1289999999999998, 0.239))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/sketch_7_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/sketch_7_revolve_0_ortho.stl')