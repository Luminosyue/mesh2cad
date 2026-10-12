import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.5, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.63046, -0.09346)
sketch_1 = sketch_1.lineTo(-0.63167, -0.03545)
sketch_1 = sketch_1.lineTo(-0.63101, 0.01082)
sketch_1 = sketch_1.threePointArc((-0.63099, 0.02986), (-0.63115, 0.04796))
sketch_1 = sketch_1.lineTo(-0.63004, 0.09683)
sketch_1 = sketch_1.lineTo(-0.62991, 0.11405)
sketch_1 = sketch_1.lineTo(-0.63046, -0.09346)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.629, 0.041, 0.501), axisEnd=(-0.626, 1.041, 0.501))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_6_revolve_2_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_6_revolve_2_ortho.stl')