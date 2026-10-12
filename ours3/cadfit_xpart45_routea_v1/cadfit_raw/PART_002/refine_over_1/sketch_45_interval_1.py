import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.14265, -0.1247, -0.93116), normal=(0.05995, 0.00015, -0.9982), xDir=(0.0, -1.0, -0.00015))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.25283, 0.13599)
loop_1 = loop_1.lineTo(-0.2542, 0.11483)
loop_1 = loop_1.lineTo(-0.2544, 0.07775)
loop_1 = loop_1.lineTo(-0.25045, -0.004)
loop_1 = loop_1.lineTo(-0.24873, -0.0335)
loop_1 = loop_1.lineTo(-0.24475, -0.07059)
loop_1 = loop_1.threePointArc((-0.24094, -0.09007), (-0.23756, -0.10767))
loop_1 = loop_1.lineTo(-0.27379, -0.11696)
loop_1 = loop_1.lineTo(-0.2635, 0.01197)
loop_1 = loop_1.lineTo(-0.25292, 0.13494)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_45_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_45_interval_1.stl')