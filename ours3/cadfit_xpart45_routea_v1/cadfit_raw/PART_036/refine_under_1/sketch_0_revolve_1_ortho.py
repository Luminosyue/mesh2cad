import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.0, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.01215, 0.17239)
sketch_1 = sketch_1.lineTo(-0.01218, 0.15205)
sketch_1 = sketch_1.lineTo(0.00922, 0.15705)
sketch_1 = sketch_1.threePointArc((0.01426, 0.1573), (0.01938, 0.15732))
sketch_1 = sketch_1.threePointArc((0.0312, 0.15764), (0.04242, 0.15822))
sketch_1 = sketch_1.threePointArc((0.06892, 0.15932), (0.08953, 0.1601))
sketch_1 = sketch_1.lineTo(0.10011, 0.16025)
sketch_1 = sketch_1.lineTo(0.11396, 0.15846)
sketch_1 = sketch_1.lineTo(0.12756, 0.15501)
sketch_1 = sketch_1.lineTo(0.13724, 0.17498)
sketch_1 = sketch_1.lineTo(-0.01215, 0.17239)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.063, 0.175, 0.001), axisEnd=(-0.9369999999999999, 0.157, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_0_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_0_revolve_1_ortho.stl')