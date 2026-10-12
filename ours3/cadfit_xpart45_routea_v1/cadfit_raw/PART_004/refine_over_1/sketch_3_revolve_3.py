import cadquery as cq
import math

# Plane definition from JSON
origin = (0.415, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.03567, -96.01654)
sketch_1 = sketch_1.circle(95.81023)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.037, -0.205, 0.416), axisEnd=(1.037, -0.205, 0.416))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_3_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_3_revolve_3.stl')