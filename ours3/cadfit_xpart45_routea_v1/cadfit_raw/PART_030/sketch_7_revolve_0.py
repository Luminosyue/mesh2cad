import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 1.0, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.55759, 0.42905)
sketch_1 = sketch_1.circle(2e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.559, 0.43, 1.001), axisEnd=(1.5579999999999998, 0.447, 1.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_030/sketch_7_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_030/sketch_7_revolve_0.stl')