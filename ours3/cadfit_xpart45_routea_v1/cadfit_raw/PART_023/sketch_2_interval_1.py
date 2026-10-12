import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.07845, 0.65337, 0.01068), normal=(-0.50643, 0.86228, 0.00129), xDir=(0.86228, 0.50643, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.25308, -0.2316)
loop_1 = loop_1.lineTo(0.23479, -0.23548)
loop_1 = loop_1.lineTo(0.22348, -0.24118)
loop_1 = loop_1.lineTo(0.20304, -0.26573)
loop_1 = loop_1.lineTo(0.19543, -0.27744)
loop_1 = loop_1.threePointArc((0.19536, -0.2913), (0.1962, -0.30165))
loop_1 = loop_1.lineTo(0.20383, -0.31672)
loop_1 = loop_1.lineTo(0.21751, -0.33101)
loop_1 = loop_1.lineTo(0.25121, -0.33625)
loop_1 = loop_1.lineTo(0.26176, -0.33101)
loop_1 = loop_1.threePointArc((0.27278, -0.32056), (0.28089, -0.31251))
loop_1 = loop_1.lineTo(0.29063, -0.28701)
loop_1 = loop_1.lineTo(0.28885, -0.2705)
loop_1 = loop_1.lineTo(0.28656, -0.25444)
loop_1 = loop_1.lineTo(0.25343, -0.23165)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/sketch_2_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/sketch_2_interval_1.stl')