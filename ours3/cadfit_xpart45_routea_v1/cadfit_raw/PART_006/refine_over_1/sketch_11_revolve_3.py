import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.596)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.04492, -1810.99484)
sketch_1 = sketch_1.circle(1811.84751)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.044, 0.854, 0.597), axisEnd=(0.956, 0.854, 0.597))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_11_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_11_revolve_3.stl')