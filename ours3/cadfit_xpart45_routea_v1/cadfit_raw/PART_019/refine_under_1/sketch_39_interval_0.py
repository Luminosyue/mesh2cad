import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01289, 0.74937, 0.01061), normal=(-0.00085, -1.0, -0.00117), xDir=(-1.0, 0.00085, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.96098, -0.11827)
loop_1 = loop_1.lineTo(-0.94989, -0.1751)
loop_1 = loop_1.lineTo(-0.93582, -0.23492)
loop_1 = loop_1.lineTo(-0.91959, -0.29539)
loop_1 = loop_1.lineTo(-0.91129, -0.35795)
loop_1 = loop_1.lineTo(-0.9026, -0.39127)
loop_1 = loop_1.lineTo(-0.87952, -0.44115)
loop_1 = loop_1.lineTo(-0.89659, -0.41678)
loop_1 = loop_1.lineTo(-0.91868, -0.38013)
loop_1 = loop_1.lineTo(-0.92508, -0.36791)
loop_1 = loop_1.lineTo(-0.93269, -0.35509)
loop_1 = loop_1.threePointArc((-0.94156, -0.32447), (-0.95055, -0.29341))
loop_1 = loop_1.threePointArc((-0.95528, -0.26116), (-0.95991, -0.23173))
loop_1 = loop_1.threePointArc((-0.96067, -0.20498), (-0.96196, -0.18274))
loop_1 = loop_1.lineTo(-0.96261, -0.16649)
loop_1 = loop_1.lineTo(-0.96223, -0.14245)
loop_1 = loop_1.lineTo(-0.96116, -0.12184)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.52)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_39_interval_0.stl')