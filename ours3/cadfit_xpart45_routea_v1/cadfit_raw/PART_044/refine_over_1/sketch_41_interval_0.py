import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.97597), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07814, 0.62468)
loop_1 = loop_1.lineTo(-0.05188, 0.66375)
loop_1 = loop_1.threePointArc((-0.05448, 0.65514), (-0.05735, 0.64637))
loop_1 = loop_1.threePointArc((-0.06048, 0.63596), (-0.06327, 0.62603))
loop_1 = loop_1.lineTo(-0.06785, 0.60884)
loop_1 = loop_1.threePointArc((-0.06794, 0.60227), (-0.06785, 0.59597))
loop_1 = loop_1.lineTo(-0.06532, 0.56743)
loop_1 = loop_1.lineTo(-0.06106, 0.54808)
loop_1 = loop_1.lineTo(-0.05703, 0.51652)
loop_1 = loop_1.threePointArc((-0.05773, 0.50415), (-0.05848, 0.49994))
loop_1 = loop_1.lineTo(-0.12949, 0.54752)
loop_1 = loop_1.lineTo(-0.07821, 0.62457)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.64)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_41_interval_0.stl')