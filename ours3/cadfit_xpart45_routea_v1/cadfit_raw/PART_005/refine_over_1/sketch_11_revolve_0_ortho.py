import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.591)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.23158, 85.94584)
sketch_1 = sketch_1.circle(85.08971)
sketch_1 = sketch_1.moveTo(0.10395, 1.31494)
sketch_1 = sketch_1.circle(0.45874)
sketch_1 = sketch_1.moveTo(0.28589, 22.80943)
sketch_1 = sketch_1.circle(21.95331)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.053, 0.858, 0.592), axisEnd=(-0.947, 0.858, 0.592))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_11_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_11_revolve_0_ortho.stl')