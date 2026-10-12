import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.16712, -0.10155)
loop_1 = loop_1.lineTo(0.18112, -0.11343)
loop_1 = loop_1.lineTo(0.19291, -0.13038)
loop_1 = loop_1.lineTo(0.19104, -0.14479)
loop_1 = loop_1.lineTo(0.17879, -0.15913)
loop_1 = loop_1.lineTo(0.12141, -0.14811)
loop_1 = loop_1.lineTo(0.10616, -0.15059)
loop_1 = loop_1.lineTo(0.09179, -0.15132)
loop_1 = loop_1.lineTo(0.0752, -0.14848)
loop_1 = loop_1.lineTo(0.06304, -0.14576)
loop_1 = loop_1.lineTo(0.05295, -0.14321)
loop_1 = loop_1.lineTo(0.16764, -0.09725)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_40_interval_0.stl')