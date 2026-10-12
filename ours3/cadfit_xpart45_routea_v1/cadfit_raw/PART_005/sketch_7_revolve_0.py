import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 1.0, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.03055, -0.31475)
sketch_1 = sketch_1.circle(0.00015)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.031, -0.314, 1.001), axisEnd=(0.023, 0.686, 1.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/sketch_7_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/sketch_7_revolve_0.stl')