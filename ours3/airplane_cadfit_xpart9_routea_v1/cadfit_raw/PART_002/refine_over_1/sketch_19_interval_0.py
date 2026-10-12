import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.63102, 0.09794, 0.00999), normal=(0.35495, -0.93449, 0.02703), xDir=(-0.93484, -0.35508, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17589, 0.21396)
loop_1 = loop_1.threePointArc((0.18079, 0.1114), (0.18564, 0.01295))
loop_1 = loop_1.lineTo(0.09109, 0.01295)
loop_1 = loop_1.lineTo(0.10124, 0.01924)
loop_1 = loop_1.lineTo(0.13226, 0.04269)
loop_1 = loop_1.lineTo(0.14608, 0.07735)
loop_1 = loop_1.lineTo(0.14738, 0.08814)
loop_1 = loop_1.lineTo(0.14864, 0.11087)
loop_1 = loop_1.lineTo(0.14775, 0.12169)
loop_1 = loop_1.lineTo(0.14689, 0.1444)
loop_1 = loop_1.threePointArc((0.15139, 0.15973), (0.1556, 0.17284))
loop_1 = loop_1.lineTo(0.17293, 0.209)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_19_interval_0.stl')