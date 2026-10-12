import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.72078, 0.29806, -0.06841), normal=(-0.93113, -0.36469, 0.00075), xDir=(-0.36469, 0.93113, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.11696, 0.24227)
loop_1 = loop_1.threePointArc((0.0867, 0.24186), (0.0577, 0.24029))
loop_1 = loop_1.lineTo(0.03485, 0.24046)
loop_1 = loop_1.lineTo(-0.04697, 0.23938)
loop_1 = loop_1.threePointArc((-0.08947, 0.2384), (-0.12778, 0.23804))
loop_1 = loop_1.lineTo(-0.15846, 0.23709)
loop_1 = loop_1.threePointArc((-0.21654, 0.23413), (-0.27112, 0.23227))
loop_1 = loop_1.lineTo(0.28204, 0.22978)
loop_1 = loop_1.lineTo(0.26938, 0.23343)
loop_1 = loop_1.lineTo(0.24316, 0.23556)
loop_1 = loop_1.lineTo(0.19317, 0.24097)
loop_1 = loop_1.lineTo(0.14485, 0.24122)
loop_1 = loop_1.lineTo(0.12253, 0.24208)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.49)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_32_interval_0.stl')