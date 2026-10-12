import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.417, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.01212, 0.31385)
sketch_1 = sketch_1.threePointArc((0.05299, 0.3135), (0.11549, 0.31411))
sketch_1 = sketch_1.threePointArc((0.22041, 0.31321), (0.32054, 0.31374))
sketch_1 = sketch_1.lineTo(0.38947, 0.31403)
sketch_1 = sketch_1.threePointArc((0.48577, 0.31343), (0.57762, 0.31409))
sketch_1 = sketch_1.threePointArc((0.66716, 0.31365), (0.75251, 0.31449))
sketch_1 = sketch_1.threePointArc((0.77192, 0.3141), (0.79144, 0.31307))
sketch_1 = sketch_1.lineTo(0.82445, 0.30754)
sketch_1 = sketch_1.lineTo(0.8401, 0.30059)
sketch_1 = sketch_1.threePointArc((0.84953, 0.2935), (0.85825, 0.28731))
sketch_1 = sketch_1.lineTo(0.85708, 0.32692)
sketch_1 = sketch_1.lineTo(-0.01212, 0.31385)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.418, 0.321, 0.418), axisEnd=(-0.582, 0.306, 0.418))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_6_revolve_2_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_6_revolve_2_ortho.stl')