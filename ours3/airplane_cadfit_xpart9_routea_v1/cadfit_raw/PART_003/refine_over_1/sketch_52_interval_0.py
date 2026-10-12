import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.21959), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02015, 0.50302)
loop_1 = loop_1.lineTo(0.0209, 0.07898)
loop_1 = loop_1.threePointArc((0.02622, 0.10684), (0.03296, 0.13525))
loop_1 = loop_1.lineTo(0.04531, 0.18894)
loop_1 = loop_1.threePointArc((0.05864, 0.23923), (0.07408, 0.29081))
loop_1 = loop_1.threePointArc((0.08594, 0.33246), (0.09686, 0.37223))
loop_1 = loop_1.threePointArc((0.10281, 0.39265), (0.10731, 0.41223))
loop_1 = loop_1.lineTo(0.12203, 0.47059)
loop_1 = loop_1.lineTo(0.12995, 0.50302)
loop_1 = loop_1.lineTo(0.02048, 0.50302)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_52_interval_0.stl')