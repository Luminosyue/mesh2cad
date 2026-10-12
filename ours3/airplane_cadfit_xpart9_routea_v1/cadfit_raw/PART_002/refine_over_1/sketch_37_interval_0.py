import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.11815, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.04013, 0.19847)
loop_1 = loop_1.lineTo(0.05363, 0.2297)
loop_1 = loop_1.threePointArc((0.05955, 0.24583), (0.06493, 0.26128))
loop_1 = loop_1.threePointArc((0.07132, 0.27636), (0.07704, 0.29084))
loop_1 = loop_1.threePointArc((0.08392, 0.3035), (0.08648, 0.30822))
loop_1 = loop_1.lineTo(0.09675, 0.32844)
loop_1 = loop_1.threePointArc((0.10128, 0.334), (0.10523, 0.33947))
loop_1 = loop_1.lineTo(0.1202, 0.35513)
loop_1 = loop_1.lineTo(0.13809, 0.36687)
loop_1 = loop_1.lineTo(0.07786, 0.3734)
loop_1 = loop_1.lineTo(0.04117, 0.20539)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.88)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_37_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_37_interval_0.stl')