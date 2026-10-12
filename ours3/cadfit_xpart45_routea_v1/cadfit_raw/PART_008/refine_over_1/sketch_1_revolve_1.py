import cadquery as cq
import math

# Plane definition from JSON
origin = (0.298, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.8273, 0.3321)
sketch_1 = sketch_1.threePointArc((-0.02096, 1.13058), (-0.80787, 0.32243))
sketch_1 = sketch_1.lineTo(0.82625, 0.33209)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.011, 0.321, 0.299), axisEnd=(1.011, 0.321, 0.299))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_1_revolve_1.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_1_revolve_1.stl')