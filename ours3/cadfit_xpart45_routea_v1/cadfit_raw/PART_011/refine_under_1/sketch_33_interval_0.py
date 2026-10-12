import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.80326, -0.25052, -0.02709), normal=(-0.96225, 0.27216, 0.00118), xDir=(0.27216, 0.96225, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16525, 0.26669)
loop_1 = loop_1.lineTo(-0.15105, 0.26637)
loop_1 = loop_1.lineTo(-0.11971, 0.26629)
loop_1 = loop_1.lineTo(-0.10881, 0.2662)
loop_1 = loop_1.lineTo(-0.06081, 0.26561)
loop_1 = loop_1.lineTo(-0.0385, 0.26473)
loop_1 = loop_1.lineTo(-0.01528, 0.26533)
loop_1 = loop_1.threePointArc((0.0231, 0.26491), (0.05617, 0.265))
loop_1 = loop_1.lineTo(0.07301, 0.26416)
loop_1 = loop_1.lineTo(0.11561, 0.26345)
loop_1 = loop_1.lineTo(0.1347, 0.26355)
loop_1 = loop_1.lineTo(0.19201, 0.2613)
loop_1 = loop_1.threePointArc((0.21435, 0.26052), (0.2329, 0.25974))
loop_1 = loop_1.lineTo(0.27301, 0.24828)
loop_1 = loop_1.lineTo(-0.16641, 0.26661)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.68)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_33_interval_0.stl')