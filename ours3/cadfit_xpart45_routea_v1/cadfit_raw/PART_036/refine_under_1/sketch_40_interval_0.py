import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.47525, 0.14615, 0.10101), normal=(0.01988, -0.75052, -0.66054), xDir=(-0.99965, -0.02649, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.49564, 0.11353)
loop_1 = loop_1.threePointArc((-0.47987, 0.11347), (-0.46344, 0.11326))
loop_1 = loop_1.lineTo(-0.45124, 0.11229)
loop_1 = loop_1.lineTo(-0.45127, 0.08254)
loop_1 = loop_1.threePointArc((-0.45149, 0.07331), (-0.45172, 0.06495))
loop_1 = loop_1.threePointArc((-0.45217, 0.05198), (-0.45242, 0.04647))
loop_1 = loop_1.lineTo(-0.48996, 0.03809)
loop_1 = loop_1.lineTo(-0.49655, 0.07009)
loop_1 = loop_1.lineTo(-0.49626, 0.09208)
loop_1 = loop_1.lineTo(-0.49647, 0.10471)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_40_interval_0.stl')