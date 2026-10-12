import cadquery as cq
import math

# Plane definition from JSON
origin = (0.869, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(17.44008, -0.46903)
sketch_1 = sketch_1.circle(17.42129)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.02, -0.497, 0.87), axisEnd=(0.02, 0.503, 0.87))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_044/cadfit/raw/part_044/sketch_0_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_044/cadfit/raw/part_044/sketch_0_revolve_3.stl')