import cadquery as cq
import math

# Plane definition from JSON
origin = (0.234, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.82786, 0.36829)
sketch_1 = sketch_1.circle(0.00011)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.829, 0.369, 0.23500000000000001), axisEnd=(0.838, -0.631, 0.23500000000000001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_041/sketch_3_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_041/sketch_3_revolve_0.stl')