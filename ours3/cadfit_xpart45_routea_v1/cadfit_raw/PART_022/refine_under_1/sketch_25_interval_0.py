import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.59139, -0.06909, 0.05948), normal=(1.0, -0.0, -0.0), xDir=(-0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.72061, 0.07901)
loop_1 = loop_1.lineTo(0.72229, 0.05313)
loop_1 = loop_1.threePointArc((0.72412, 0.03278), (0.72545, 0.01433))
loop_1 = loop_1.lineTo(0.72605, 0.00399)
loop_1 = loop_1.lineTo(0.72597, -0.00945)
loop_1 = loop_1.lineTo(0.72761, -0.04273)
loop_1 = loop_1.lineTo(0.72647, -0.0951)
loop_1 = loop_1.threePointArc((0.72658, -0.11158), (0.72707, -0.1249))
loop_1 = loop_1.lineTo(0.72758, -0.14179)
loop_1 = loop_1.lineTo(0.72725, -0.15731)
loop_1 = loop_1.lineTo(0.72061, -0.16953)
loop_1 = loop_1.lineTo(0.72061, 0.07651)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_25_interval_0.stl')