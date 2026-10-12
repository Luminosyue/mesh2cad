import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.121)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.78211, 0.02666)
sketch_1 = sketch_1.lineTo(-0.78211, 0.00907)
sketch_1 = sketch_1.lineTo(-0.78196, 0.02666)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.781, 0.009999999999999998, 0.122), axisEnd=(0.219, 0.009999999999999998, 0.122))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_001/cadfit/raw/part_001/sketch_4_revolve_2.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_001/cadfit/raw/part_001/sketch_4_revolve_2.stl')