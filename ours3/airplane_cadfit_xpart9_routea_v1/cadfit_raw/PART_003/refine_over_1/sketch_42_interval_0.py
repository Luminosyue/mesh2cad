import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.29386, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.11, 0.34274)
loop_1 = loop_1.lineTo(0.10965, 0.17784)
loop_1 = loop_1.lineTo(0.09473, 0.20953)
loop_1 = loop_1.threePointArc((0.09039, 0.21872), (0.08595, 0.22724))
loop_1 = loop_1.threePointArc((0.07991, 0.23903), (0.07396, 0.2501))
loop_1 = loop_1.lineTo(0.05594, 0.27949)
loop_1 = loop_1.threePointArc((0.04615, 0.29417), (0.04216, 0.29916))
loop_1 = loop_1.lineTo(0.02621, 0.3193)
loop_1 = loop_1.lineTo(0.01127, 0.33416)
loop_1 = loop_1.lineTo(-0.0, 0.34274)
loop_1 = loop_1.lineTo(0.10984, 0.34274)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.13)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_42_interval_0.stl')