import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.188)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(5393.15328, -0.02452)
sketch_1 = sketch_1.circle(5393.41398)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.26, -0.013000000000000001, 0.189), axisEnd=(-0.26, 0.987, 0.189))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_11_revolve_2_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_11_revolve_2_ortho.stl')