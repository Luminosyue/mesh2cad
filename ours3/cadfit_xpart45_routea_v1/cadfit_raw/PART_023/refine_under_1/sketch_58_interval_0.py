import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.1253, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30191, -0.33901)
loop_1 = loop_1.threePointArc((0.30214, -0.35406), (0.30213, -0.36973))
loop_1 = loop_1.lineTo(0.30352, -0.40895)
loop_1 = loop_1.threePointArc((0.30375, -0.43518), (0.30447, -0.46018))
loop_1 = loop_1.lineTo(0.31211, -0.48442)
loop_1 = loop_1.lineTo(0.31548, -0.49498)
loop_1 = loop_1.threePointArc((0.32149, -0.50777), (0.32733, -0.51984))
loop_1 = loop_1.lineTo(0.32773, -0.53752)
loop_1 = loop_1.lineTo(0.3218, -0.55623)
loop_1 = loop_1.lineTo(0.31019, -0.57123)
loop_1 = loop_1.lineTo(0.30515, -0.58237)
loop_1 = loop_1.lineTo(0.30193, -0.33919)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_58_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_58_interval_0.stl')