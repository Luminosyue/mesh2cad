import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.391)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.38008, 0.72191)
sketch_1 = sketch_1.circle(0.58193)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.191, 0.838, 0.392), axisEnd=(-0.797, 0.987, 0.392))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/sketch_11_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/sketch_11_revolve_1_ortho.stl')