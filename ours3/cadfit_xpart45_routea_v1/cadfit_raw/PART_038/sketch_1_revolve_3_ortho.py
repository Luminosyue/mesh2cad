import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.0, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.26293, -0.00034)
sketch_1 = sketch_1.threePointArc((0.26283, -0.02121), (0.26289, -0.04125))
sketch_1 = sketch_1.lineTo(0.26249, -0.08052)
sketch_1 = sketch_1.lineTo(0.262, -0.09629)
sketch_1 = sketch_1.threePointArc((0.25745, -0.10682), (0.25529, -0.10944))
sketch_1 = sketch_1.lineTo(0.24024, -0.12382)
sketch_1 = sketch_1.lineTo(0.20307, -0.1193)
sketch_1 = sketch_1.lineTo(0.18901, -0.09937)
sketch_1 = sketch_1.lineTo(0.18732, -0.08801)
sketch_1 = sketch_1.threePointArc((0.18686, -0.08059), (0.18659, -0.07285))
sketch_1 = sketch_1.threePointArc((0.18639, -0.06756), (0.1861, -0.06268))
sketch_1 = sketch_1.lineTo(0.18554, -0.04445)
sketch_1 = sketch_1.lineTo(0.18507, -0.01544)
sketch_1 = sketch_1.threePointArc((0.1847, -0.00811), (0.18449, -0.00068))
sketch_1 = sketch_1.lineTo(0.26293, -0.00034)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.225, 0.0, 0.001), axisEnd=(-0.775, -0.004, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/sketch_1_revolve_3_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/sketch_1_revolve_3_ortho.stl')