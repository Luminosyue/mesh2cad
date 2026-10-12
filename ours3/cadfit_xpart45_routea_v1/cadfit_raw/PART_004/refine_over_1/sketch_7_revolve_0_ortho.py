import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.378, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(30.76324, 0.74952)
sketch_1 = sketch_1.circle(30.74753)
sketch_1 = sketch_1.moveTo(4266.4244, 0.07935)
sketch_1 = sketch_1.circle(4266.40869)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.017, 0.416, 0.379), axisEnd=(0.017, 1.416, 0.379))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_7_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_7_revolve_0_ortho.stl')