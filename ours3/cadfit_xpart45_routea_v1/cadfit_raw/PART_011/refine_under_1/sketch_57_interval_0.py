import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.69558, -0.48249, -0.01777), normal=(-0.86978, 0.49324, 0.014), xDir=(0.49329, 0.86986, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.43671, 0.18838)
loop_1 = loop_1.threePointArc((0.43242, 0.01933), (0.42758, -0.15675))
loop_1 = loop_1.lineTo(0.42714, -0.17105)
loop_1 = loop_1.lineTo(0.43396, -0.15967)
loop_1 = loop_1.threePointArc((0.43581, -0.1378), (0.43818, -0.11507))
loop_1 = loop_1.threePointArc((0.43977, -0.0888), (0.44081, -0.06696))
loop_1 = loop_1.lineTo(0.44017, -0.03929)
loop_1 = loop_1.threePointArc((0.44125, -0.01509), (0.44242, 0.00656))
loop_1 = loop_1.lineTo(0.44132, 0.02926)
loop_1 = loop_1.lineTo(0.44191, 0.05477)
loop_1 = loop_1.lineTo(0.44334, 0.07737)
loop_1 = loop_1.lineTo(0.44496, 0.15509)
loop_1 = loop_1.lineTo(0.44498, 0.17359)
loop_1 = loop_1.lineTo(0.43705, 0.1879)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_57_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_57_interval_0.stl')