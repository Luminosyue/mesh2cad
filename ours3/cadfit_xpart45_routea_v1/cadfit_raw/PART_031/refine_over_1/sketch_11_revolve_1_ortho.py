import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.622)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(940.08648, 0.36542)
sketch_1 = sketch_1.circle(939.30743)
sketch_1 = sketch_1.moveTo(386.94531, -0.12335)
sketch_1 = sketch_1.circle(386.16627)
sketch_1 = sketch_1.moveTo(5.07524, -0.48493)
sketch_1 = sketch_1.circle(4.29619)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.78, -0.08, 0.623), axisEnd=(0.78, 0.92, 0.623))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_11_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_11_revolve_1_ortho.stl')