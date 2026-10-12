import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.0, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.99887, 0.00286)
sketch_1 = sketch_1.threePointArc((-0.99395, -0.00833), (-0.98459, -0.01542))
sketch_1 = sketch_1.threePointArc((-0.97268, -0.01777), (-0.96231, -0.01724))
sketch_1 = sketch_1.lineTo(0.10884, -0.01819)
sketch_1 = sketch_1.lineTo(0.7338, -0.0196)
sketch_1 = sketch_1.threePointArc((0.75811, -0.02352), (0.78019, -0.02339))
sketch_1 = sketch_1.lineTo(0.8104, -0.03142)
sketch_1 = sketch_1.threePointArc((0.83533, -0.0324), (0.85783, -0.03138))
sketch_1 = sketch_1.threePointArc((0.87401, -0.03537), (0.88819, -0.04207))
sketch_1 = sketch_1.threePointArc((0.90262, -0.04448), (0.91533, -0.04402))
sketch_1 = sketch_1.lineTo(0.98292, -0.04469)
sketch_1 = sketch_1.threePointArc((0.9917, -0.0424), (0.99548, -0.03626))
sketch_1 = sketch_1.threePointArc((0.9992, -0.02851), (0.99922, -0.02167))
sketch_1 = sketch_1.threePointArc((0.99994, -0.00843), (0.9999, 0.00281))
sketch_1 = sketch_1.lineTo(-0.99887, 0.00286)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.016, 0.004, 0.001), axisEnd=(-0.984, 0.004, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_1_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_1_revolve_0_ortho.stl')