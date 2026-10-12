import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0125, -0.28579, -0.12479), normal=(-0.57108, 0.8209, 0.00186), xDir=(0.8209, 0.57108, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.77281, 0.38509)
loop_1 = loop_1.threePointArc((0.77283, 0.29504), (0.77284, 0.20124))
loop_1 = loop_1.threePointArc((0.77421, 0.21344), (0.77527, 0.22339))
loop_1 = loop_1.lineTo(0.78707, 0.24843)
loop_1 = loop_1.lineTo(0.78892, 0.2598)
loop_1 = loop_1.lineTo(0.7926, 0.27435)
loop_1 = loop_1.lineTo(0.79175, 0.28813)
loop_1 = loop_1.lineTo(0.78945, 0.29983)
loop_1 = loop_1.lineTo(0.78505, 0.31594)
loop_1 = loop_1.lineTo(0.77505, 0.34774)
loop_1 = loop_1.threePointArc((0.77337, 0.36604), (0.77292, 0.37998))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_29_interval_0.stl')