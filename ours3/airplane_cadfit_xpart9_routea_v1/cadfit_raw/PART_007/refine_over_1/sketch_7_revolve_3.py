import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.898, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-58.95982, 0.05577)
sketch_1 = sketch_1.circle(58.45277)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.506, 0.057, 0.899), axisEnd=(-0.506, -0.943, 0.899))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_7_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_7_revolve_3.stl')