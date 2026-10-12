import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.96)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.39519, -0.09594)
sketch_1 = sketch_1.circle(0.00015)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.394, -0.095, 0.961), axisEnd=(-0.389, 0.905, 0.961))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_11_revolve_3_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_11_revolve_3_ortho.stl')