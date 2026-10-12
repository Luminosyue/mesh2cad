import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.39885, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.36212, -0.50202)
loop_1 = loop_1.lineTo(0.36167, -0.77725)
loop_1 = loop_1.threePointArc((0.36048, -0.77073), (0.35891, -0.76475))
loop_1 = loop_1.lineTo(0.35185, -0.74761)
loop_1 = loop_1.lineTo(0.34318, -0.72895)
loop_1 = loop_1.lineTo(0.32585, -0.69139)
loop_1 = loop_1.threePointArc((0.32679, -0.67325), (0.32794, -0.65457))
loop_1 = loop_1.lineTo(0.33937, -0.61027)
loop_1 = loop_1.threePointArc((0.34375, -0.59466), (0.34773, -0.5798))
loop_1 = loop_1.lineTo(0.35287, -0.54715)
loop_1 = loop_1.lineTo(0.36133, -0.5055)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.71)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_58_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_58_interval_0.stl')