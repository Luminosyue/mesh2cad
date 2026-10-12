import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.59605, 0.48151, -0.00486), normal=(-0.57745, 0.81606, 0.02444), xDir=(0.8163, 0.57763, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.49669, 0.17329)
loop_1 = loop_1.lineTo(0.50685, 0.16064)
loop_1 = loop_1.lineTo(0.5169, 0.13378)
loop_1 = loop_1.lineTo(0.51748, 0.09867)
loop_1 = loop_1.lineTo(0.51483, 0.04758)
loop_1 = loop_1.lineTo(0.50957, 0.00027)
loop_1 = loop_1.threePointArc((0.50657, -0.0243), (0.50347, -0.04569))
loop_1 = loop_1.lineTo(0.5001, -0.09381)
loop_1 = loop_1.lineTo(0.50219, -0.10846)
loop_1 = loop_1.lineTo(0.50653, -0.14192)
loop_1 = loop_1.lineTo(0.50143, -0.15245)
loop_1 = loop_1.lineTo(0.48702, -0.17567)
loop_1 = loop_1.lineTo(0.48392, -0.19004)
loop_1 = loop_1.lineTo(0.47025, -0.20067)
loop_1 = loop_1.lineTo(0.49639, 0.16909)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_35_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_35_interval_2.stl')