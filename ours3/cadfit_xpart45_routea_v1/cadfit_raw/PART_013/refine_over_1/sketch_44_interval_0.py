import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.57026, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.963, 0.22736)
loop_1 = loop_1.lineTo(0.22197, 0.2054)
loop_1 = loop_1.lineTo(0.38251, 0.20588)
loop_1 = loop_1.lineTo(0.90937, 0.2249)
loop_1 = loop_1.lineTo(0.53742, 0.20757)
loop_1 = loop_1.lineTo(0.96218, 0.22732)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_44_interval_0.stl')