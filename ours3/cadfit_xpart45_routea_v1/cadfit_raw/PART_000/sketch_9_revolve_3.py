import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, -0.0)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.99766, 0.00857)
sketch_1 = sketch_1.lineTo(0.99008, 0.01961)
sketch_1 = sketch_1.threePointArc((0.97344, 0.02334), (0.95809, 0.02287))
sketch_1 = sketch_1.lineTo(-0.73697, 0.0274)
sketch_1 = sketch_1.threePointArc((-0.76176, 0.03068), (-0.78437, 0.03021))
sketch_1 = sketch_1.threePointArc((-0.79655, 0.03404), (-0.80721, 0.03838))
sketch_1 = sketch_1.threePointArc((-0.83522, 0.03908), (-0.86053, 0.03774))
sketch_1 = sketch_1.threePointArc((-0.87556, 0.04166), (-0.88861, 0.04803))
sketch_1 = sketch_1.threePointArc((-0.90195, 0.051), (-0.91372, 0.05073))
sketch_1 = sketch_1.lineTo(-0.98565, 0.05144)
sketch_1 = sketch_1.threePointArc((-0.99464, 0.04577), (-0.99805, 0.04187))
sketch_1 = sketch_1.threePointArc((-0.99975, 0.02124), (-0.99977, 0.00276))
sketch_1 = sketch_1.lineTo(0.99766, 0.00857)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.019, 0.004, 0.001), axisEnd=(0.981, 0.004, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_9_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_9_revolve_3.stl')