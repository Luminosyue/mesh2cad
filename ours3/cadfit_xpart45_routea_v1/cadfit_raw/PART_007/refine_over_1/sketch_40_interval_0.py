import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.36423, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11711, 0.59646)
loop_1 = loop_1.threePointArc((-0.2043, 0.59562), (-0.29513, 0.59571))
loop_1 = loop_1.lineTo(-0.46329, 0.59374)
loop_1 = loop_1.threePointArc((-0.51791, 0.59376), (-0.56979, 0.5929))
loop_1 = loop_1.threePointArc((-0.60838, 0.59337), (-0.64485, 0.59268))
loop_1 = loop_1.threePointArc((-0.68284, 0.59338), (-0.71872, 0.59207))
loop_1 = loop_1.threePointArc((-0.8054, 0.59272), (-0.88802, 0.59187))
loop_1 = loop_1.lineTo(-0.92461, 0.59246)
loop_1 = loop_1.lineTo(-0.96177, 0.58827)
loop_1 = loop_1.threePointArc((-0.96736, 0.58096), (-0.96997, 0.5767))
loop_1 = loop_1.lineTo(-0.97, 0.59635)
loop_1 = loop_1.lineTo(-0.11769, 0.59635)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.97)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_40_interval_0.stl')