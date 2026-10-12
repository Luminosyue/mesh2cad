import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.11128, 0.94374, -0.08149), normal=(0.10231, -0.99475, -0.00123), xDir=(-0.99475, -0.10231, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.21002, -0.22691)
loop_1 = loop_1.lineTo(-0.20985, -0.18154)
loop_1 = loop_1.lineTo(-0.31947, -0.18154)
loop_1 = loop_1.lineTo(-0.31894, 0.17846)
loop_1 = loop_1.lineTo(0.31263, 0.17846)
loop_1 = loop_1.lineTo(0.31317, -0.18154)
loop_1 = loop_1.lineTo(0.20796, -0.18154)
loop_1 = loop_1.lineTo(0.20818, -0.22701)
loop_1 = loop_1.lineTo(-0.19943, -0.22691)
loop_1 = loop_1.lineTo(-0.21002, -0.22691)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.63)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_21_interval_0.stl')