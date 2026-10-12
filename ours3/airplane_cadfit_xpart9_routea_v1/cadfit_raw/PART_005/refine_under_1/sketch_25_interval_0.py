import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0216, -0.58421, 0.1498), normal=(-0.02357, 0.10143, -0.99456), xDir=(0.0, -0.99484, -0.10146))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.24633, 0.01212)
loop_1 = loop_1.lineTo(0.06515, -0.0209)
loop_1 = loop_1.lineTo(0.04461, -0.02394)
loop_1 = loop_1.lineTo(0.02205, -0.02798)
loop_1 = loop_1.lineTo(-0.40114, -0.10421)
loop_1 = loop_1.lineTo(-0.38401, -0.10664)
loop_1 = loop_1.lineTo(-0.09652, -0.10606)
loop_1 = loop_1.lineTo(0.03312, -0.08237)
loop_1 = loop_1.lineTo(0.07237, -0.07586)
loop_1 = loop_1.lineTo(0.09949, -0.0617)
loop_1 = loop_1.threePointArc((0.10501, -0.06041), (0.11075, -0.05906))
loop_1 = loop_1.lineTo(0.17521, -0.05616)
loop_1 = loop_1.threePointArc((0.18709, -0.05151), (0.19973, -0.0474))
loop_1 = loop_1.threePointArc((0.20771, -0.04552), (0.21356, -0.04446))
loop_1 = loop_1.lineTo(0.22415, -0.03668)
loop_1 = loop_1.threePointArc((0.2272, -0.02681), (0.23045, -0.01657))
loop_1 = loop_1.lineTo(0.24447, 0.00754)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_25_interval_0.stl')