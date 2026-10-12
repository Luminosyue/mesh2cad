import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.25), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.89643, -0.32972)
loop_1 = loop_1.lineTo(0.9104, -0.31574)
loop_1 = loop_1.lineTo(0.94464, -0.27722)
loop_1 = loop_1.lineTo(0.97319, -0.22016)
loop_1 = loop_1.threePointArc((0.98383, -0.16488), (0.99316, -0.11201))
loop_1 = loop_1.lineTo(0.9981, -0.07584)
loop_1 = loop_1.lineTo(0.99646, -0.02453)
loop_1 = loop_1.threePointArc((0.99049, 0.04457), (0.98513, 0.11622))
loop_1 = loop_1.lineTo(0.97513, 0.16465)
loop_1 = loop_1.lineTo(0.96062, 0.19609)
loop_1 = loop_1.lineTo(0.96891, 0.16639)
loop_1 = loop_1.lineTo(0.98575, 0.04956)
loop_1 = loop_1.threePointArc((0.99139, -0.01234), (0.98975, -0.07667))
loop_1 = loop_1.threePointArc((0.98319, -0.09982), (0.97438, -0.1228))
loop_1 = loop_1.threePointArc((0.969, -0.16955), (0.96052, -0.21727))
loop_1 = loop_1.threePointArc((0.94065, -0.26664), (0.90988, -0.31222))
loop_1 = loop_1.threePointArc((0.90354, -0.321), (0.89666, -0.32945))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.46)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_69_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_69_interval_0.stl')