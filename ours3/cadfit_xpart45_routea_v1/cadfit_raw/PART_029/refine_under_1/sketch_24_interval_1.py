import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05097, -0.03511, -0.036), normal=(-0.0, -0.54698, 0.83714), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.01801, -0.06184)
loop_1 = loop_1.lineTo(-1.03238, -0.06865)
loop_1 = loop_1.lineTo(-1.03985, -0.07994)
loop_1 = loop_1.threePointArc((-1.04358, -0.09024), (-1.04704, -0.10018))
loop_1 = loop_1.threePointArc((-1.04894, -0.11793), (-1.04969, -0.13118))
loop_1 = loop_1.lineTo(-1.04316, -0.11108)
loop_1 = loop_1.lineTo(-0.97908, -0.12638)
loop_1 = loop_1.threePointArc((-0.97964, -0.11476), (-0.98016, -0.1049))
loop_1 = loop_1.threePointArc((-0.98395, -0.09417), (-0.98728, -0.08515))
loop_1 = loop_1.lineTo(-1.00007, -0.06798)
loop_1 = loop_1.threePointArc((-1.01092, -0.06288), (-1.01669, -0.06203))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_24_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_24_interval_1.stl')