import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.39), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.674, -0.98282)
loop_1 = loop_1.threePointArc((-0.6628, -0.98485), (-0.65192, -0.98588))
loop_1 = loop_1.lineTo(-0.4335, -0.9887)
loop_1 = loop_1.lineTo(-0.25062, -0.98616)
loop_1 = loop_1.lineTo(-0.11927, -0.98516)
loop_1 = loop_1.lineTo(-0.01402, -0.98589)
loop_1 = loop_1.lineTo(0.10718, -0.98506)
loop_1 = loop_1.threePointArc((0.20528, -0.98588), (0.29876, -0.98542))
loop_1 = loop_1.threePointArc((0.35314, -0.98514), (0.40462, -0.98321))
loop_1 = loop_1.lineTo(-0.67333, -0.98303)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.68)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_70_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_70_interval_0.stl')