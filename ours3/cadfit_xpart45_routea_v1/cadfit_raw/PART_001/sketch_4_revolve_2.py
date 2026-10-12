import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.5, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.00084, -0.06869)
sketch_1 = sketch_1.circle(0.01923)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.002, -0.069, -0.499), axisEnd=(1.0019999999999998, -0.06, -0.499))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_4_revolve_2.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_4_revolve_2.stl')