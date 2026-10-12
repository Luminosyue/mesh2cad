import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05333, 0.54334, -0.17161), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.97868, 0.1384)
loop_1 = loop_1.lineTo(-0.95066, 0.13755)
loop_1 = loop_1.lineTo(-0.85984, 0.13764)
loop_1 = loop_1.lineTo(-0.79852, 0.13105)
loop_1 = loop_1.threePointArc((-0.79223, 0.12711), (-0.78795, 0.12447))
loop_1 = loop_1.threePointArc((-0.7768, 0.11872), (-0.7679, 0.11488))
loop_1 = loop_1.lineTo(-0.76138, 0.09736)
loop_1 = loop_1.lineTo(-1.00054, 0.12728)
loop_1 = loop_1.lineTo(-0.97868, 0.1384)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.37)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_21_interval_0.stl')