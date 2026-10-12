import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.006, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.96575, 0.32922)
sketch_1 = sketch_1.lineTo(0.96668, 0.27473)
sketch_1 = sketch_1.lineTo(0.96023, 0.28506)
sketch_1 = sketch_1.threePointArc((0.94334, 0.2977), (0.92739, 0.30893))
sketch_1 = sketch_1.lineTo(0.86836, 0.31381)
sketch_1 = sketch_1.lineTo(0.59801, 0.31278)
sketch_1 = sketch_1.lineTo(0.49346, 0.31245)
sketch_1 = sketch_1.lineTo(0.21844, 0.31176)
sketch_1 = sketch_1.lineTo(0.05265, 0.31249)
sketch_1 = sketch_1.lineTo(-0.09218, 0.31238)
sketch_1 = sketch_1.lineTo(0.96575, 0.32922)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.428, 0.322, -0.005), axisEnd=(-0.572, 0.306, -0.005))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_5_revolve_2_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_5_revolve_2_ortho.stl')