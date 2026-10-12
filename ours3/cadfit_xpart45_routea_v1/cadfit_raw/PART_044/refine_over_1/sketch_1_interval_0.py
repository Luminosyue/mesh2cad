import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.27603, -0.00895, -0.06804), normal=(0.04625, 0.99893, -0.00088), xDir=(0.99893, -0.04625, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.34445, 0.58037)
loop_1 = loop_1.lineTo(0.33287, 0.5617)
loop_1 = loop_1.lineTo(0.32908, 0.55161)
loop_1 = loop_1.lineTo(0.32295, 0.54149)
loop_1 = loop_1.lineTo(0.31278, 0.52194)
loop_1 = loop_1.threePointArc((0.3146, 0.5073), (0.31611, 0.49774))
loop_1 = loop_1.lineTo(0.31642, 0.48087)
loop_1 = loop_1.lineTo(0.32251, 0.46069)
loop_1 = loop_1.lineTo(0.32365, 0.4506)
loop_1 = loop_1.lineTo(0.32688, 0.44046)
loop_1 = loop_1.threePointArc((0.33401, 0.43749), (0.3395, 0.43534))
loop_1 = loop_1.lineTo(0.35133, 0.59272)
loop_1 = loop_1.lineTo(0.34445, 0.58037)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_1_interval_0.stl')