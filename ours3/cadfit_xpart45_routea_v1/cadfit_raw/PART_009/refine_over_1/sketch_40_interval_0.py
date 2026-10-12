import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.92349, 0.1186, 0.05645), normal=(-0.99351, 0.11375, 0.00032), xDir=(0.11375, 0.99351, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34504, 0.57666)
loop_1 = loop_1.lineTo(-0.30445, 0.57666)
loop_1 = loop_1.lineTo(-0.32225, 0.5414)
loop_1 = loop_1.lineTo(-0.33104, 0.52194)
loop_1 = loop_1.threePointArc((-0.33343, 0.50147), (-0.33606, 0.48238))
loop_1 = loop_1.lineTo(-0.33772, 0.46995)
loop_1 = loop_1.threePointArc((-0.33976, 0.44566), (-0.34129, 0.42442))
loop_1 = loop_1.lineTo(-0.34323, 0.40665)
loop_1 = loop_1.lineTo(-0.34524, 0.38601)
loop_1 = loop_1.lineTo(-0.34504, 0.57503)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_40_interval_0.stl')