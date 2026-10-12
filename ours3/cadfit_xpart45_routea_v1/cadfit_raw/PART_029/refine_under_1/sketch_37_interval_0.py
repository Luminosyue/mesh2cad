import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.23435, 0.09563, 0.22387), normal=(0.0, -0.94574, -0.32492), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.12131, 0.41776)
loop_1 = loop_1.threePointArc((1.12846, 0.41702), (1.1359, 0.41621))
loop_1 = loop_1.lineTo(1.1538, 0.40973)
loop_1 = loop_1.lineTo(1.16491, 0.40601)
loop_1 = loop_1.lineTo(1.17934, 0.39887)
loop_1 = loop_1.lineTo(1.19339, 0.38805)
loop_1 = loop_1.lineTo(1.2026, 0.37162)
loop_1 = loop_1.lineTo(1.20642, 0.35969)
loop_1 = loop_1.lineTo(1.21059, 0.32595)
loop_1 = loop_1.lineTo(1.20975, 0.31331)
loop_1 = loop_1.lineTo(1.01072, 0.31331)
loop_1 = loop_1.lineTo(1.04338, 0.36215)
loop_1 = loop_1.threePointArc((1.05764, 0.37799), (1.06385, 0.38421))
loop_1 = loop_1.threePointArc((1.07126, 0.38997), (1.07818, 0.39511))
loop_1 = loop_1.lineTo(1.12131, 0.41776)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_37_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_37_interval_0.stl')