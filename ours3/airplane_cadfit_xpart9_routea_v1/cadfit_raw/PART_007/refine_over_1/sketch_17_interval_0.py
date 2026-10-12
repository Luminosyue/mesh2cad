import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03401, 0.04287, -0.05301), normal=(0.01372, 0.1215, 0.9925), xDir=(0.0, 0.99259, -0.12151))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.90107, -0.76962)
loop_1 = loop_1.lineTo(-0.46662, -0.88499)
loop_1 = loop_1.threePointArc((-0.4837, -0.8823), (-0.49679, -0.88003))
loop_1 = loop_1.lineTo(-0.51769, -0.87759)
loop_1 = loop_1.threePointArc((-0.54227, -0.87342), (-0.56208, -0.87033))
loop_1 = loop_1.lineTo(-0.62295, -0.8597)
loop_1 = loop_1.lineTo(-0.6861, -0.84919)
loop_1 = loop_1.lineTo(-0.70716, -0.84601)
loop_1 = loop_1.threePointArc((-0.74165, -0.83932), (-0.77326, -0.83234))
loop_1 = loop_1.threePointArc((-0.80019, -0.82418), (-0.82272, -0.8163))
loop_1 = loop_1.lineTo(-0.83618, -0.8114)
loop_1 = loop_1.lineTo(-0.8507, -0.80418)
loop_1 = loop_1.lineTo(-0.87561, -0.79145)
loop_1 = loop_1.lineTo(-0.89098, -0.77934)
loop_1 = loop_1.lineTo(-0.90107, -0.76962)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_17_interval_0.stl')