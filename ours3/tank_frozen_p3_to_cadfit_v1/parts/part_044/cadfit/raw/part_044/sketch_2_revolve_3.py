import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.213, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-23905.86664, -0.1934)
sketch_1 = sketch_1.circle(23905.28886)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.577, -0.192, 0.214), axisEnd=(-0.577, -1.1920000000000002, 0.214))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_044/cadfit/raw/part_044/sketch_2_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_044/cadfit/raw/part_044/sketch_2_revolve_3.stl')