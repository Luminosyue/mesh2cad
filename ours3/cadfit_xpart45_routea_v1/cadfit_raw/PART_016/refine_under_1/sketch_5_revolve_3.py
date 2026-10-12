import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.0, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.35519, 0.31728)
sketch_1 = sketch_1.lineTo(0.4104, 0.31641)
sketch_1 = sketch_1.lineTo(0.44515, 0.31683)
sketch_1 = sketch_1.lineTo(0.49426, 0.31668)
sketch_1 = sketch_1.threePointArc((0.42011, 0.3177), (0.34879, 0.31709))
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.417, 0.317, 0.001), axisEnd=(1.4169999999999998, 0.318, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_5_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_5_revolve_3.stl')