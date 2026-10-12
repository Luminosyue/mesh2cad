import cadquery as cq
import math

# Plane definition from JSON
origin = (0.993, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.278, 0.07193)
sketch_1 = sketch_1.circle(0.00465)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.279, 0.068, 0.994), axisEnd=(-0.721, 0.051000000000000004, 0.994))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_3_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_3_revolve_0_ortho.stl')