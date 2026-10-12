import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.425)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.23354, -0.20043)
sketch_1 = sketch_1.circle(2e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.23500000000000001, -0.199, 0.426), axisEnd=(1.2269999999999999, -0.321, 0.426))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_11_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_11_revolve_0.stl')