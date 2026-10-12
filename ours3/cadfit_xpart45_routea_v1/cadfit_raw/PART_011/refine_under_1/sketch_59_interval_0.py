import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.52, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.77503, 0.21728)
loop_1 = loop_1.lineTo(0.77578, -0.15408)
loop_1 = loop_1.lineTo(0.78713, -0.09577)
loop_1 = loop_1.lineTo(0.78618, -0.04485)
loop_1 = loop_1.lineTo(0.78728, 0.00499)
loop_1 = loop_1.threePointArc((0.78705, 0.05089), (0.78758, 0.09845))
loop_1 = loop_1.lineTo(0.78665, 0.14773)
loop_1 = loop_1.lineTo(0.78361, 0.19235)
loop_1 = loop_1.lineTo(0.77511, 0.21705)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.29)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_59_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_59_interval_0.stl')