import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 1.0)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.31593, -0.10261)
sketch_1 = sketch_1.circle(3e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.315, -0.102, 1.001), axisEnd=(0.685, -0.097, 1.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/sketch_10_revolve_2.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/sketch_10_revolve_2.stl')