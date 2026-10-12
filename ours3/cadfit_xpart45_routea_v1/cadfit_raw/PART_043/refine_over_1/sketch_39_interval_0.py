import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.50924, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.39049, 0.14)
loop_1 = loop_1.lineTo(-0.30509, 0.13949)
loop_1 = loop_1.lineTo(-0.30562, 0.00063)
loop_1 = loop_1.lineTo(-0.32005, 0.01682)
loop_1 = loop_1.threePointArc((-0.33421, 0.03938), (-0.3483, 0.06328))
loop_1 = loop_1.threePointArc((-0.35587, 0.07721), (-0.3633, 0.09022))
loop_1 = loop_1.lineTo(-0.37538, 0.1121)
loop_1 = loop_1.threePointArc((-0.38333, 0.12647), (-0.39114, 0.14139))
loop_1 = loop_1.threePointArc((-0.4056, 0.16626), (-0.41968, 0.18973))
loop_1 = loop_1.threePointArc((-0.42629, 0.19911), (-0.43275, 0.20885))
loop_1 = loop_1.threePointArc((-0.43727, 0.21558), (-0.44238, 0.22112))
loop_1 = loop_1.lineTo(-0.46124, 0.23027)
loop_1 = loop_1.threePointArc((-0.47494, 0.23295), (-0.48126, 0.2307))
loop_1 = loop_1.lineTo(-0.49197, 0.22711)
loop_1 = loop_1.lineTo(-0.41659, 0.2673)
loop_1 = loop_1.lineTo(-0.39054, 0.14025)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.82)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_39_interval_0.stl')