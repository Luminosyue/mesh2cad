import cadquery as cq
import math

# Plane definition from JSON
origin = (0.994, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(2636.18133, 0.19978)
sketch_1 = sketch_1.circle(2636.16543)
sketch_1 = sketch_1.moveTo(339.46619, -0.4148)
sketch_1 = sketch_1.circle(339.4503)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.017, -0.106, 0.995), axisEnd=(0.017, 0.894, 0.995))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_3_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_3_revolve_0_ortho.stl')