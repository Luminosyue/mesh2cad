import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.763, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.57657, 0.12743)
sketch_1 = sketch_1.circle(3e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.578, 0.128, 0.764), axisEnd=(0.578, 1.128, 0.764))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/sketch_6_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/sketch_6_revolve_0.stl')