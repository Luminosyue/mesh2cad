import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.187, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.08412, -0.12737)
sketch_1 = sketch_1.circle(3e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.083, -0.126, 0.188), axisEnd=(-0.083, 0.874, 0.188))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_7_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_7_revolve_0.stl')