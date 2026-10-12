import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.695, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10958, -0.54461)
loop_1 = loop_1.lineTo(0.12677, -0.52979)
loop_1 = loop_1.lineTo(0.66602, -0.53125)
loop_1 = loop_1.threePointArc((0.6729, -0.53797), (0.68002, -0.54323))
loop_1 = loop_1.lineTo(0.69193, -0.55278)
loop_1 = loop_1.lineTo(0.10217, -0.55153)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.37)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_64_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_64_interval_0.stl')