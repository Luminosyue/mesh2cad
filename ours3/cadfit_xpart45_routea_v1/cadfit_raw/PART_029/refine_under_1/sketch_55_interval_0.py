import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.13, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.96704, -0.10722)
loop_1 = loop_1.threePointArc((0.95961, -0.10749), (0.95248, -0.10787))
loop_1 = loop_1.lineTo(0.9381, -0.115)
loop_1 = loop_1.lineTo(0.92875, -0.13034)
loop_1 = loop_1.threePointArc((0.92848, -0.13602), (0.92811, -0.14186))
loop_1 = loop_1.lineTo(0.99171, -0.13127)
loop_1 = loop_1.lineTo(0.99746, -0.14834)
loop_1 = loop_1.lineTo(0.99696, -0.13003)
loop_1 = loop_1.threePointArc((0.99137, -0.12138), (0.9872, -0.11569))
loop_1 = loop_1.threePointArc((0.97402, -0.10911), (0.9671, -0.10723))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.29)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_55_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_55_interval_0.stl')