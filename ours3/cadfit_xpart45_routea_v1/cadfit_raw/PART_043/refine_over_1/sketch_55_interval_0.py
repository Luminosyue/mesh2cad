import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.21231), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10114, 0.9911)
loop_1 = loop_1.lineTo(0.10551, 0.43951)
loop_1 = loop_1.threePointArc((0.12417, 0.48032), (0.13984, 0.52003))
loop_1 = loop_1.lineTo(0.14601, 0.54614)
loop_1 = loop_1.threePointArc((0.14722, 0.55948), (0.14896, 0.57289))
loop_1 = loop_1.threePointArc((0.14956, 0.58599), (0.1508, 0.59916))
loop_1 = loop_1.threePointArc((0.14999, 0.6376), (0.1503, 0.67722))
loop_1 = loop_1.threePointArc((0.15191, 0.70143), (0.15424, 0.72618))
loop_1 = loop_1.threePointArc((0.15389, 0.75356), (0.15339, 0.77942))
loop_1 = loop_1.lineTo(0.14887, 0.85824)
loop_1 = loop_1.lineTo(0.14899, 0.87714)
loop_1 = loop_1.lineTo(0.1479, 0.95631)
loop_1 = loop_1.lineTo(0.15372, 0.98026)
loop_1 = loop_1.threePointArc((0.16441, 0.98686), (0.16776, 0.98816))
loop_1 = loop_1.lineTo(0.12185, 0.99181)
loop_1 = loop_1.lineTo(0.10154, 0.99111)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_55_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_55_interval_0.stl')