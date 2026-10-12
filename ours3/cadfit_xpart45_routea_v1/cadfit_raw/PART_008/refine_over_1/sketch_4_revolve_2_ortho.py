import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.43, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.85616, 0.32834)
sketch_1 = sketch_1.lineTo(0.85691, 0.28784)
sketch_1 = sketch_1.lineTo(0.82902, 0.30235)
sketch_1 = sketch_1.lineTo(0.78756, 0.30939)
sketch_1 = sketch_1.lineTo(0.76778, 0.31326)
sketch_1 = sketch_1.lineTo(0.53314, 0.31159)
sketch_1 = sketch_1.lineTo(0.38112, 0.3114)
sketch_1 = sketch_1.lineTo(0.14604, 0.31226)
sketch_1 = sketch_1.lineTo(-0.19943, 0.31307)
sketch_1 = sketch_1.lineTo(0.85616, 0.32834)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.332, 0.322, -0.429), axisEnd=(-0.667, 0.307, -0.429))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_4_revolve_2_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_4_revolve_2_ortho.stl')