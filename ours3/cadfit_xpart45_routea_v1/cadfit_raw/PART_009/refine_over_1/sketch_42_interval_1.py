import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.26108, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.85952, 0.5202)
loop_1 = loop_1.lineTo(0.85256, 0.45138)
loop_1 = loop_1.lineTo(0.85475, 0.40825)
loop_1 = loop_1.threePointArc((0.85454, 0.32205), (0.85544, 0.23988))
loop_1 = loop_1.threePointArc((0.85469, 0.19639), (0.85319, 0.15174))
loop_1 = loop_1.lineTo(0.83577, 0.09998)
loop_1 = loop_1.threePointArc((0.82102, 0.07711), (0.80793, 0.05517))
loop_1 = loop_1.threePointArc((0.80289, 0.04907), (0.79706, 0.04425))
loop_1 = loop_1.threePointArc((0.76802, 0.02085), (0.73766, -0.00239))
loop_1 = loop_1.lineTo(0.75169, -0.02105)
loop_1 = loop_1.lineTo(0.77876, -0.0489)
loop_1 = loop_1.lineTo(0.79078, -0.05497)
loop_1 = loop_1.lineTo(0.8026, -0.05906)
loop_1 = loop_1.lineTo(0.82936, -0.08311)
loop_1 = loop_1.lineTo(0.83031, 0.07842)
loop_1 = loop_1.lineTo(0.859, -0.15194)
loop_1 = loop_1.lineTo(0.85952, 0.52019)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_42_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_42_interval_1.stl')