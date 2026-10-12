import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.0, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.89801, 0.04517)
sketch_1 = sketch_1.threePointArc((0.884, 0.04206), (0.87111, 0.03719))
sketch_1 = sketch_1.threePointArc((0.85339, 0.03586), (0.83643, 0.03729))
sketch_1 = sketch_1.threePointArc((0.81125, 0.03656), (0.78932, 0.03087))
sketch_1 = sketch_1.lineTo(0.74572, 0.02915)
sketch_1 = sketch_1.lineTo(0.72272, 0.02405)
sketch_1 = sketch_1.lineTo(-0.98573, 0.02287)
sketch_1 = sketch_1.threePointArc((-0.99508, 0.01552), (-0.99889, 0.00595))
sketch_1 = sketch_1.threePointArc((0.02884, -0.79492), (1.00015, 0.00566))
sketch_1 = sketch_1.lineTo(0.99856, 0.02872)
sketch_1 = sketch_1.lineTo(0.99364, 0.03964)
sketch_1 = sketch_1.threePointArc((0.969, 0.0446), (0.95142, 0.04387))
sketch_1 = sketch_1.threePointArc((0.92519, 0.04448), (0.89947, 0.04545))
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.016, 0.004, 0.001), axisEnd=(1.0159999999999998, 0.005, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_1_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_1_revolve_3.stl')