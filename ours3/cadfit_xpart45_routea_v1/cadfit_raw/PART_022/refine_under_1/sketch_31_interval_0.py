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
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.76)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_31_interval_0.stl')