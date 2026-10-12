import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.52858, -0.54544)
loop_1 = loop_1.lineTo(0.52884, -0.66937)
loop_1 = loop_1.threePointArc((0.53719, -0.65825), (0.54496, -0.64749))
loop_1 = loop_1.lineTo(0.54679, -0.63666)
loop_1 = loop_1.lineTo(0.54716, -0.62123)
loop_1 = loop_1.lineTo(0.54399, -0.60676)
loop_1 = loop_1.lineTo(0.54222, -0.59581)
loop_1 = loop_1.lineTo(0.53586, -0.58067)
loop_1 = loop_1.threePointArc((0.53392, -0.57559), (0.532, -0.57036))
loop_1 = loop_1.threePointArc((0.53044, -0.55788), (0.52863, -0.54604))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_53_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_53_interval_0.stl')