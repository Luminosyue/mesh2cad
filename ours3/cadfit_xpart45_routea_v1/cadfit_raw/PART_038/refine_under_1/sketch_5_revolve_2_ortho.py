import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.0, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.73347, -0.10403)
sketch_1 = sketch_1.lineTo(0.95644, -0.10458)
sketch_1 = sketch_1.threePointArc((0.84931, -0.14933), (0.7404, -0.10846))
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.847, -0.11, 0.001), axisEnd=(1.847, -0.125, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/refine_under_1/sketch_5_revolve_2_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/refine_under_1/sketch_5_revolve_2_ortho.stl')