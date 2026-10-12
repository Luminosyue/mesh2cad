import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.006, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.41003, 0.31179)
sketch_1 = sketch_1.lineTo(0.227, 0.31165)
sketch_1 = sketch_1.threePointArc((0.14918, 0.31219), (0.07522, 0.31187))
sketch_1 = sketch_1.threePointArc((0.03884, 0.31247), (0.00466, 0.31214))
sketch_1 = sketch_1.threePointArc((-0.03283, 0.31246), (-0.06806, 0.31201))
sketch_1 = sketch_1.lineTo(-0.14692, 0.3133)
sketch_1 = sketch_1.lineTo(0.40989, 0.33074)
sketch_1 = sketch_1.lineTo(0.41003, 0.31179)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.411, 0.322, -0.005), axisEnd=(0.404, 1.321, -0.005))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_5_revolve_3_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_5_revolve_3_ortho.stl')