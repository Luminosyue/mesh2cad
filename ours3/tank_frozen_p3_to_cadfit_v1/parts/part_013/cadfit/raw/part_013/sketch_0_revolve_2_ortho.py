import cadquery as cq
import math

# Plane definition from JSON
origin = (0.854, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(290.28617, -0.0744)
sketch_1 = sketch_1.circle(290.17134)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.116, -0.073, 0.855), axisEnd=(0.116, 0.927, 0.855))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_013/cadfit/raw/part_013/sketch_0_revolve_2_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_013/cadfit/raw/part_013/sketch_0_revolve_2_ortho.stl')