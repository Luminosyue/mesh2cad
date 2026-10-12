import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.30765, 0.41902, -0.12174), normal=(0.00024, -0.99531, -0.09677), xDir=(-1.0, -0.00024, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.25446, 0.0823)
loop_1 = loop_1.lineTo(1.27421, 0.0714)
loop_1 = loop_1.lineTo(1.28423, 0.06274)
loop_1 = loop_1.threePointArc((1.28005, 0.05517), (1.26981, 0.05561))
loop_1 = loop_1.lineTo(1.22475, 0.05556)
loop_1 = loop_1.lineTo(1.20816, 0.05484)
loop_1 = loop_1.lineTo(1.21602, 0.06669)
loop_1 = loop_1.lineTo(1.22597, 0.07675)
loop_1 = loop_1.threePointArc((1.23146, 0.07924), (1.2372, 0.08177))
loop_1 = loop_1.lineTo(1.25446, 0.0823)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_14_interval_0.stl')