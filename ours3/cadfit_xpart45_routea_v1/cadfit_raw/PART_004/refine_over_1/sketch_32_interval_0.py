import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.25048, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.41114, 0.73833)
loop_1 = loop_1.threePointArc((0.41318, 0.66152), (0.41241, 0.58148))
loop_1 = loop_1.threePointArc((0.41421, 0.17115), (0.41426, -0.25557))
loop_1 = loop_1.lineTo(0.40973, -0.27407)
loop_1 = loop_1.threePointArc((0.4099, -0.24211), (0.411, -0.20954))
loop_1 = loop_1.threePointArc((0.41037, -0.17095), (0.41103, -0.13149))
loop_1 = loop_1.threePointArc((0.41034, -0.06336), (0.41075, 0.0069))
loop_1 = loop_1.lineTo(0.41034, 0.09242)
loop_1 = loop_1.threePointArc((0.41106, 0.17632), (0.41105, 0.25622))
loop_1 = loop_1.lineTo(0.41114, 0.41249)
loop_1 = loop_1.lineTo(0.4107, 0.58357)
loop_1 = loop_1.lineTo(0.41109, 0.73632)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_32_interval_0.stl')