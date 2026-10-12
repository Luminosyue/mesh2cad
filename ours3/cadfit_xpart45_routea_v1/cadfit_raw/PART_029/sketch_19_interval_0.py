import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.14, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.96703, -0.10722)
loop_1 = loop_1.threePointArc((0.97418, -0.10915), (0.9816, -0.11125))
loop_1 = loop_1.threePointArc((0.99178, -0.12195), (0.99605, -0.12812))
loop_1 = loop_1.lineTo(0.99871, -0.14478)
loop_1 = loop_1.threePointArc((0.99428, -0.15643), (0.99297, -0.15906))
loop_1 = loop_1.lineTo(0.9812, -0.16911)
loop_1 = loop_1.threePointArc((0.97407, -0.17067), (0.96669, -0.17218))
loop_1 = loop_1.lineTo(0.95247, -0.17149)
loop_1 = loop_1.lineTo(0.93815, -0.16469)
loop_1 = loop_1.threePointArc((0.93049, -0.15144), (0.92789, -0.14446))
loop_1 = loop_1.threePointArc((0.92842, -0.13708), (0.92875, -0.13008))
loop_1 = loop_1.lineTo(0.93749, -0.11558)
loop_1 = loop_1.lineTo(0.94791, -0.11003)
loop_1 = loop_1.threePointArc((0.95978, -0.10749), (0.96697, -0.10721))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/sketch_19_interval_0.stl')