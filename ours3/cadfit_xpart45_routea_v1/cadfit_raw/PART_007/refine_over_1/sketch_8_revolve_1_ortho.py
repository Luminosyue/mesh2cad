import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, -0.627)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.84577, 8.09433)
sketch_1 = sketch_1.circle(7.96546)
sketch_1 = sketch_1.moveTo(-0.65882, 0.1293)
sketch_1 = sketch_1.lineTo(-0.60187, 0.12938)
sketch_1 = sketch_1.lineTo(-0.6262, 0.13041)
sketch_1 = sketch_1.lineTo(-0.65878, 0.12931)
sketch_1 = sketch_1.close()
sketch_1 = sketch_1.moveTo(-0.46752, 0.58698)
sketch_1 = sketch_1.circle(0.4584)
sketch_1 = sketch_1.moveTo(0.79486, 0.76603)
sketch_1 = sketch_1.circle(0.63706)
sketch_1 = sketch_1.moveTo(0.94794, 0.4072)
sketch_1 = sketch_1.circle(0.27819)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.039, 0.131, -0.626), axisEnd=(-1.0390000000000001, 0.131, -0.626))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_8_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_8_revolve_1_ortho.stl')