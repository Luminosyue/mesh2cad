import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35287, -0.69138)
loop_1 = loop_1.threePointArc((-0.34999, -0.69877), (-0.34711, -0.70651))
loop_1 = loop_1.threePointArc((-0.3358, -0.71368), (-0.32923, -0.71762))
loop_1 = loop_1.lineTo(-0.31166, -0.72157)
loop_1 = loop_1.threePointArc((-0.30368, -0.72126), (-0.29602, -0.7209))
loop_1 = loop_1.lineTo(-0.2622, -0.70538)
loop_1 = loop_1.threePointArc((-0.25836, -0.69749), (-0.25476, -0.68987))
loop_1 = loop_1.threePointArc((-0.25441, -0.68094), (-0.25397, -0.67323))
loop_1 = loop_1.threePointArc((-0.25635, -0.66378), (-0.25844, -0.65618))
loop_1 = loop_1.lineTo(-0.27244, -0.64282)
loop_1 = loop_1.lineTo(-0.29788, -0.63407)
loop_1 = loop_1.threePointArc((-0.30562, -0.63398), (-0.31306, -0.63398))
loop_1 = loop_1.threePointArc((-0.3218, -0.6361), (-0.32946, -0.63784))
loop_1 = loop_1.lineTo(-0.34673, -0.65073)
loop_1 = loop_1.threePointArc((-0.35236, -0.66458), (-0.35402, -0.6717))
loop_1 = loop_1.lineTo(-0.35287, -0.69138)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_10_interval_0.stl')