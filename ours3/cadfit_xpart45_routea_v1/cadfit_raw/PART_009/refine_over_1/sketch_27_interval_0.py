import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.30374, 0.88199, 0.31909), normal=(0.28698, -0.95793, 0.00292), xDir=(-0.95794, -0.28698, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.32293, 0.83933)
loop_1 = loop_1.lineTo(0.32194, 0.72011)
loop_1 = loop_1.threePointArc((0.3208, 0.72717), (0.31991, 0.73262))
loop_1 = loop_1.threePointArc((0.31408, 0.75984), (0.30876, 0.78461))
loop_1 = loop_1.lineTo(0.28869, 0.83665)
loop_1 = loop_1.lineTo(0.32128, 0.83933)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_27_interval_0.stl')