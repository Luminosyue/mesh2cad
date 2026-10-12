import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.14)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.2207, -0.01483)
sketch_1 = sketch_1.circle(0.00036)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.222, -0.013000000000000001, 0.14100000000000001), axisEnd=(1.222, -0.013999999999999999, 0.14100000000000001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_008/sketch_10_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_008/sketch_10_revolve_3.stl')