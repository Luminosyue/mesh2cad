import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.1253, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30193, 0.81112)
loop_1 = loop_1.lineTo(0.30411, 0.77007)
loop_1 = loop_1.threePointArc((0.30561, 0.74916), (0.30736, 0.72932))
loop_1 = loop_1.threePointArc((0.30682, 0.71607), (0.30694, 0.70357))
loop_1 = loop_1.threePointArc((0.3056, 0.68533), (0.30326, 0.66666))
loop_1 = loop_1.lineTo(0.3022, 0.65379)
loop_1 = loop_1.threePointArc((0.30532, 0.63993), (0.30943, 0.62714))
loop_1 = loop_1.threePointArc((0.31541, 0.61522), (0.32108, 0.60281))
loop_1 = loop_1.lineTo(0.32269, 0.57718)
loop_1 = loop_1.threePointArc((0.32069, 0.56865), (0.31904, 0.56064))
loop_1 = loop_1.threePointArc((0.31192, 0.53918), (0.30588, 0.52648))
loop_1 = loop_1.threePointArc((0.30373, 0.51267), (0.30187, 0.49963))
loop_1 = loop_1.lineTo(0.30193, 0.8109)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_57_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_57_interval_0.stl')