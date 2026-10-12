import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.19373, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00824, 0.89161)
loop_1 = loop_1.threePointArc((0.03037, 0.89089), (0.0534, 0.8896))
loop_1 = loop_1.threePointArc((0.06093, 0.8893), (0.06858, 0.88872))
loop_1 = loop_1.lineTo(0.10945, 0.88388)
loop_1 = loop_1.lineTo(0.14325, 0.88047)
loop_1 = loop_1.lineTo(0.20283, 0.87185)
loop_1 = loop_1.lineTo(0.25371, 0.86508)
loop_1 = loop_1.lineTo(0.25982, 0.89164)
loop_1 = loop_1.lineTo(0.00842, 0.89164)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_82_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_82_interval_1.stl')