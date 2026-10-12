import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.34526, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02741, 0.30207)
loop_1 = loop_1.lineTo(-0.01565, 0.30687)
loop_1 = loop_1.lineTo(-0.05296, 0.04226)
loop_1 = loop_1.threePointArc((-0.04437, 0.05717), (-0.03761, 0.07161))
loop_1 = loop_1.threePointArc((-0.03007, 0.08666), (-0.02328, 0.10108))
loop_1 = loop_1.threePointArc((-0.00795, 0.13479), (0.00635, 0.16711))
loop_1 = loop_1.threePointArc((0.01167, 0.18088), (0.0175, 0.19484))
loop_1 = loop_1.threePointArc((0.0226, 0.20357), (0.02689, 0.21201))
loop_1 = loop_1.lineTo(0.03566, 0.2282)
loop_1 = loop_1.threePointArc((0.04604, 0.24292), (0.05722, 0.25771))
loop_1 = loop_1.lineTo(0.0783, 0.2803)
loop_1 = loop_1.threePointArc((0.08549, 0.28442), (0.09189, 0.28877))
loop_1 = loop_1.lineTo(0.02764, 0.30204)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_30_interval_0.stl')