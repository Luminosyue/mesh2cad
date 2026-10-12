import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.319, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.94, -0.11106)
sketch_1 = sketch_1.lineTo(0.93973, -0.12566)
sketch_1 = sketch_1.threePointArc((0.93325, -0.12456), (0.92762, -0.12529))
sketch_1 = sketch_1.threePointArc((0.91355, -0.12567), (0.89961, -0.12525))
sketch_1 = sketch_1.threePointArc((0.8653, -0.12516), (0.83026, -0.12376))
sketch_1 = sketch_1.lineTo(0.60649, -0.11734)
sketch_1 = sketch_1.threePointArc((0.53723, -0.11478), (0.46579, -0.1113))
sketch_1 = sketch_1.threePointArc((0.39902, -0.10954), (0.33018, -0.10656))
sketch_1 = sketch_1.threePointArc((0.18238, -0.10171), (0.02913, -0.095))
sketch_1 = sketch_1.lineTo(0.94, -0.11106)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.479, -0.102, -0.318), axisEnd=(-0.521, -0.08499999999999999, -0.318))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_4_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_4_revolve_0_ortho.stl')