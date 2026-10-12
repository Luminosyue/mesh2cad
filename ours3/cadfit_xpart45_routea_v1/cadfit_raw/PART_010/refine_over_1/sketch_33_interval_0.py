import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.35196, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.11038, 0.86627)
loop_1 = loop_1.lineTo(0.29743, 0.8657)
loop_1 = loop_1.lineTo(0.25764, 0.85079)
loop_1 = loop_1.lineTo(0.21976, 0.82981)
loop_1 = loop_1.lineTo(0.18537, 0.81093)
loop_1 = loop_1.lineTo(0.14819, 0.80753)
loop_1 = loop_1.lineTo(0.11026, 0.80847)
loop_1 = loop_1.lineTo(0.11038, 0.86612)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.61)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_33_interval_0.stl')