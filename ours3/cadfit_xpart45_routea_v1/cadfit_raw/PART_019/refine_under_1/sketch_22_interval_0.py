import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.81284, 0.00449, 0.50121), normal=(0.87312, -0.00073, -0.4875), xDir=(-0.00084, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.78521, 0.20945)
loop_1 = loop_1.lineTo(-0.78473, -0.26168)
loop_1 = loop_1.lineTo(-0.78914, -0.24442)
loop_1 = loop_1.threePointArc((-0.7975, -0.19693), (-0.80463, -0.15206))
loop_1 = loop_1.lineTo(-0.80402, -0.13297)
loop_1 = loop_1.lineTo(-0.80468, -0.11785)
loop_1 = loop_1.lineTo(-0.80032, -0.06231)
loop_1 = loop_1.lineTo(-0.81017, 0.00869)
loop_1 = loop_1.lineTo(-0.80418, 0.07899)
loop_1 = loop_1.lineTo(-0.80478, 0.13522)
loop_1 = loop_1.threePointArc((-0.79965, 0.15456), (-0.79699, 0.16787))
loop_1 = loop_1.lineTo(-0.78656, 0.20471)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.91)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_22_interval_0.stl')