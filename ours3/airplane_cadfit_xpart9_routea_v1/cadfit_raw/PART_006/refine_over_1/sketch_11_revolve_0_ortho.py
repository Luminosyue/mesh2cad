import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.173)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.73757, 0.95187)
sketch_1 = sketch_1.circle(3e-05)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.737, 0.953, 0.174), axisEnd=(-1.0650000000000002, 1.8969999999999998, 0.174))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_11_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_11_revolve_0_ortho.stl')