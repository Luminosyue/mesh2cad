import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.59095, 0.06581, -0.54055), normal=(-0.79983, -0.01226, 0.6001), xDir=(-0.01533, 0.99988, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16391, 0.08114)
loop_1 = loop_1.lineTo(-0.19391, 0.08034)
loop_1 = loop_1.lineTo(-0.23038, 0.07661)
loop_1 = loop_1.lineTo(-0.24962, 0.04722)
loop_1 = loop_1.lineTo(-0.25224, 0.03555)
loop_1 = loop_1.lineTo(-0.25403, 0.015)
loop_1 = loop_1.lineTo(-0.25383, -0.01)
loop_1 = loop_1.lineTo(-0.25152, -0.04578)
loop_1 = loop_1.lineTo(-0.23179, -0.07676)
loop_1 = loop_1.lineTo(-0.21407, -0.0777)
loop_1 = loop_1.lineTo(-0.19539, -0.08084)
loop_1 = loop_1.threePointArc((-0.17333, -0.08109), (-0.1546, -0.08102))
loop_1 = loop_1.lineTo(-0.15358, 0.07946)
loop_1 = loop_1.lineTo(-0.16391, 0.08114)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_12_interval_0.stl')