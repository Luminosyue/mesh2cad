import cadquery as cq
import math

# Plane definition from JSON
origin = (0.298, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.82742, 0.32524)
sketch_1 = sketch_1.lineTo(0.82769, 0.30744)
sketch_1 = sketch_1.lineTo(0.76926, 0.31311)
sketch_1 = sketch_1.lineTo(0.21744, 0.31133)
sketch_1 = sketch_1.threePointArc((0.0621, 0.31115), (-0.09856, 0.31277))
sketch_1 = sketch_1.lineTo(-0.19735, 0.31257)
sketch_1 = sketch_1.threePointArc((-0.35744, 0.31359), (-0.51008, 0.3135))
sketch_1 = sketch_1.threePointArc((-0.59011, 0.31448), (-0.66588, 0.31301))
sketch_1 = sketch_1.lineTo(-0.76249, 0.31407)
sketch_1 = sketch_1.lineTo(-0.80282, 0.31122)
sketch_1 = sketch_1.lineTo(0.82742, 0.32524)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.011, 0.321, 0.299), axisEnd=(-0.989, 0.314, 0.299))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_1_revolve_2_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_1_revolve_2_ortho.stl')