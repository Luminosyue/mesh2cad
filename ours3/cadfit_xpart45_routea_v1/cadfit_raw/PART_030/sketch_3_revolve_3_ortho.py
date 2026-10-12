import cadquery as cq
import math

# Plane definition from JSON
origin = (0.963, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.08588, -0.23157)
sketch_1 = sketch_1.circle(8e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.087, -0.231, 0.964), axisEnd=(1.087, -0.229, 0.964))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_030/sketch_3_revolve_3_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_030/sketch_3_revolve_3_ortho.stl')