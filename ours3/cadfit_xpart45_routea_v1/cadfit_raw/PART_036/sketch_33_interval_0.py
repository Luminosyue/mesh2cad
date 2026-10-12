import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.29, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.15192, 0.20874)
loop_1 = loop_1.lineTo(0.16953, 0.20655)
loop_1 = loop_1.lineTo(0.18601, 0.19579)
loop_1 = loop_1.lineTo(0.19466, 0.17837)
loop_1 = loop_1.lineTo(0.19369, 0.16098)
loop_1 = loop_1.lineTo(0.18654, 0.14814)
loop_1 = loop_1.lineTo(0.16911, 0.13717)
loop_1 = loop_1.lineTo(0.15289, 0.13774)
loop_1 = loop_1.lineTo(0.14245, 0.14325)
loop_1 = loop_1.lineTo(0.12602, 0.16084)
loop_1 = loop_1.lineTo(0.12219, 0.17683)
loop_1 = loop_1.lineTo(0.1272, 0.19228)
loop_1 = loop_1.lineTo(0.15185, 0.20868)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_33_interval_0.stl')