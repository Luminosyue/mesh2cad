import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.80108), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16837, 0.40195)
loop_1 = loop_1.lineTo(0.13028, 0.40098)
loop_1 = loop_1.lineTo(0.12998, 0.36548)
loop_1 = loop_1.lineTo(0.10491, 0.37549)
loop_1 = loop_1.threePointArc((0.08567, 0.38151), (0.06725, 0.38636))
loop_1 = loop_1.threePointArc((0.05992, 0.38823), (0.05304, 0.38913))
loop_1 = loop_1.lineTo(-0.0111, 0.39863)
loop_1 = loop_1.threePointArc((-0.03487, 0.40008), (-0.05741, 0.4009))
loop_1 = loop_1.threePointArc((-0.11299, 0.40149), (-0.16605, 0.40164))
loop_1 = loop_1.threePointArc((-0.17325, 0.40136), (-0.17978, 0.40033))
loop_1 = loop_1.lineTo(-0.32314, 0.3813)
loop_1 = loop_1.lineTo(-0.31138, 0.39557)
loop_1 = loop_1.lineTo(-0.27937, 0.40265)
loop_1 = loop_1.threePointArc((-0.22495, 0.40282), (-0.16866, 0.40198))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.78)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_41_interval_0.stl')