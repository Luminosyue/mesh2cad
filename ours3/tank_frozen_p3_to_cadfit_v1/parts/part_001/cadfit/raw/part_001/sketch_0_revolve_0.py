import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.5, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.00467, -0.07039)
sketch_1 = sketch_1.circle(0.02002)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.003, -0.06999999999999999, -0.499), axisEnd=(0.71, 0.631, -0.499))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_001/cadfit/raw/part_001/sketch_0_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_001/cadfit/raw/part_001/sketch_0_revolve_0.stl')