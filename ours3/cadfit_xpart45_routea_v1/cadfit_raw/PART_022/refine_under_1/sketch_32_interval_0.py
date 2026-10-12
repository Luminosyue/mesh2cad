import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.60341, 0.58364, 0.05554), normal=(0.70109, -0.71285, -0.01785), xDir=(-0.71296, -0.7012, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30265, 0.25208)
loop_1 = loop_1.lineTo(-0.53192, 0.22887)
loop_1 = loop_1.lineTo(-0.51924, -0.20521)
loop_1 = loop_1.lineTo(0.31505, -0.20521)
loop_1 = loop_1.lineTo(0.30301, 0.23883)
loop_1 = loop_1.lineTo(0.30265, 0.25208)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.18573, 0.20486)
loop_2 = loop_2.lineTo(0.18911, 0.17432)
loop_2 = loop_2.lineTo(-0.22409, 0.1654)
loop_2 = loop_2.lineTo(-0.22302, 0.20486)
loop_2 = loop_2.lineTo(0.18132, 0.20486)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(1.8)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_32_interval_0.stl')