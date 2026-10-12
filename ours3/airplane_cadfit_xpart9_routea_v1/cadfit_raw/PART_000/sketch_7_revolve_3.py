import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.349)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.37786, -0.04568)
sketch_1 = sketch_1.circle(0.00029)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.379, -0.044, 0.35), axisEnd=(1.3789999999999998, -0.045, 0.35))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_000/sketch_7_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_000/sketch_7_revolve_3.stl')