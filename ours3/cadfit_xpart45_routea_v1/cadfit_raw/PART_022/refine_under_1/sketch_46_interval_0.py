import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.84506, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05396, 0.25154)
loop_1 = loop_1.lineTo(-0.17512, 0.24996)
loop_1 = loop_1.lineTo(-0.35167, 0.24641)
loop_1 = loop_1.threePointArc((-0.39701, 0.24565), (-0.44356, 0.2458))
loop_1 = loop_1.lineTo(-0.4706, 0.24441)
loop_1 = loop_1.lineTo(0.49488, 0.24546)
loop_1 = loop_1.threePointArc((0.45768, 0.24601), (0.41965, 0.24745))
loop_1 = loop_1.lineTo(0.34033, 0.24914)
loop_1 = loop_1.lineTo(0.17453, 0.25042)
loop_1 = loop_1.lineTo(0.01405, 0.25137)
loop_1 = loop_1.threePointArc((-0.01927, 0.25125), (-0.05329, 0.25168))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.67)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_46_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_46_interval_0.stl')