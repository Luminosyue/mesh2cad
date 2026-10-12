import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.06159, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.82732, 0.3321)
loop_1 = loop_1.lineTo(0.82769, 0.30744)
loop_1 = loop_1.lineTo(0.76926, 0.31311)
loop_1 = loop_1.lineTo(0.21744, 0.31133)
loop_1 = loop_1.threePointArc((0.0621, 0.31115), (-0.09856, 0.31277))
loop_1 = loop_1.lineTo(-0.19735, 0.31257)
loop_1 = loop_1.threePointArc((-0.35744, 0.31359), (-0.51008, 0.3135))
loop_1 = loop_1.threePointArc((-0.59011, 0.31448), (-0.66588, 0.31301))
loop_1 = loop_1.lineTo(-0.76249, 0.31407)
loop_1 = loop_1.lineTo(-0.80282, 0.31122)
loop_1 = loop_1.lineTo(-0.80788, 0.32243)
loop_1 = loop_1.lineTo(0.82625, 0.33209)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.8)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_4_interval_0.stl')