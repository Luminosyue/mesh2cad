import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03516, 0.03209, -0.17565), normal=(-0.04368, 0.99405, 0.09976), xDir=(0.99904, 0.0439, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.98711, -0.10904)
loop_1 = loop_1.lineTo(0.96964, -0.11595)
loop_1 = loop_1.lineTo(0.9595, -0.13611)
loop_1 = loop_1.lineTo(0.95877, -0.14835)
loop_1 = loop_1.lineTo(0.96924, -0.20716)
loop_1 = loop_1.lineTo(0.9866, -0.22444)
loop_1 = loop_1.threePointArc((0.99541, -0.22374), (1.00312, -0.22305))
loop_1 = loop_1.lineTo(1.01403, -0.20615)
loop_1 = loop_1.lineTo(1.01879, -0.19149)
loop_1 = loop_1.lineTo(1.02297, -0.16963)
loop_1 = loop_1.threePointArc((1.02328, -0.16146), (1.02353, -0.15362))
loop_1 = loop_1.lineTo(1.02173, -0.13659)
loop_1 = loop_1.lineTo(1.0126, -0.1186)
loop_1 = loop_1.lineTo(0.98842, -0.10923)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_20_interval_0.stl')