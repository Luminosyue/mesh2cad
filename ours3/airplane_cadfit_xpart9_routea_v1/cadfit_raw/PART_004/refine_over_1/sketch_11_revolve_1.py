import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 0.187)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.42996, -0.91863)
sketch_1 = sketch_1.lineTo(-0.42996, -0.92932)
sketch_1 = sketch_1.lineTo(-0.42987, -0.91866)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.429, -0.928, 0.188), axisEnd=(0.571, -0.928, 0.188))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_11_revolve_1.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_11_revolve_1.stl')