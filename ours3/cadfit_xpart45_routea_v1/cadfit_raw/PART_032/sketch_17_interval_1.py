import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.19, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.84984, -0.11851)
loop_1 = loop_1.lineTo(0.8861, -0.12528)
loop_1 = loop_1.lineTo(0.90312, -0.13162)
loop_1 = loop_1.lineTo(0.88429, -0.17859)
loop_1 = loop_1.lineTo(0.837, -0.21184)
loop_1 = loop_1.lineTo(0.80357, -0.20799)
loop_1 = loop_1.lineTo(0.79043, -0.20603)
loop_1 = loop_1.lineTo(0.77633, -0.19121)
loop_1 = loop_1.lineTo(0.75993, -0.178)
loop_1 = loop_1.lineTo(0.74347, -0.14261)
loop_1 = loop_1.lineTo(0.74445, -0.12951)
loop_1 = loop_1.lineTo(0.77894, -0.12028)
loop_1 = loop_1.lineTo(0.79218, -0.1195)
loop_1 = loop_1.threePointArc((0.80749, -0.11937), (0.82204, -0.11893))
loop_1 = loop_1.threePointArc((0.83565, -0.11863), (0.84969, -0.11856))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.13)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/sketch_17_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/sketch_17_interval_1.stl')