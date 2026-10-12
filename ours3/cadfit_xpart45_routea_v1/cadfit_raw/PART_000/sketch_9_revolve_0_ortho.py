import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, -0.0)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.99972, -0.00413)
sketch_1 = sketch_1.threePointArc((-0.9997, -0.02232), (-0.99843, -0.03974))
sketch_1 = sketch_1.lineTo(-0.98999, -0.05116)
sketch_1 = sketch_1.threePointArc((-0.97227, -0.05171), (-0.95681, -0.04934))
sketch_1 = sketch_1.lineTo(-0.89221, -0.04488)
sketch_1 = sketch_1.threePointArc((-0.88024, -0.04073), (-0.87087, -0.03545))
sketch_1 = sketch_1.threePointArc((-0.85899, -0.03247), (-0.84771, -0.03309))
sketch_1 = sketch_1.threePointArc((-0.8249, -0.03315), (-0.8045, -0.03176))
sketch_1 = sketch_1.threePointArc((-0.78445, -0.02561), (-0.7643, -0.02479))
sketch_1 = sketch_1.threePointArc((-0.74289, -0.02251), (-0.7242, -0.01799))
sketch_1 = sketch_1.threePointArc((-0.45711, -0.01769), (-0.18058, -0.01921))
sketch_1 = sketch_1.lineTo(0.98532, -0.01634)
sketch_1 = sketch_1.threePointArc((0.99338, -0.00935), (0.99783, -0.00413))
sketch_1 = sketch_1.lineTo(-0.99972, -0.00413)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.019, 0.004, 0.001), axisEnd=(-1.0190000000000001, 0.004, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_9_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_9_revolve_0_ortho.stl')