import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.973, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(4.27519, 0.49209)
sketch_1 = sketch_1.circle(4.28894)
sketch_1 = sketch_1.moveTo(199.64492, -0.07895)
sketch_1 = sketch_1.circle(199.65867)
sketch_1 = sketch_1.moveTo(30.06654, -0.45428)
sketch_1 = sketch_1.circle(30.0803)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.013000000000000001, -0.013000000000000001, 0.974), axisEnd=(-0.013000000000000001, 0.987, 0.974))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_7_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_7_revolve_1_ortho.stl')