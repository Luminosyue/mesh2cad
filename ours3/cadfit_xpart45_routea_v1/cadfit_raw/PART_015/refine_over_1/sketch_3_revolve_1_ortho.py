import cadquery as cq
import math

# Plane definition from JSON
origin = (0.92, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(200.96543, 0.08978)
sketch_1 = sketch_1.circle(201.02755)
sketch_1 = sketch_1.moveTo(0.11128, -0.16368)
sketch_1 = sketch_1.circle(0.17339)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.061, -0.036, 0.921), axisEnd=(-0.061, 0.964, 0.921))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_3_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_3_revolve_1_ortho.stl')