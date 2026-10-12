import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.06585, 0.04567, 0.15109), normal=(0.01655, -0.45879, -0.88839), xDir=(-0.99935, -0.03605, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.90466, 0.12551)
loop_1 = loop_1.lineTo(0.91926, 0.11862)
loop_1 = loop_1.threePointArc((0.92854, 0.10464), (0.93199, 0.09724))
loop_1 = loop_1.threePointArc((0.90105, 0.0917), (0.87032, 0.09179))
loop_1 = loop_1.lineTo(0.87392, 0.10675)
loop_1 = loop_1.lineTo(0.89034, 0.12363)
loop_1 = loop_1.threePointArc((0.89763, 0.12458), (0.90381, 0.12539))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_9_interval_0.stl')