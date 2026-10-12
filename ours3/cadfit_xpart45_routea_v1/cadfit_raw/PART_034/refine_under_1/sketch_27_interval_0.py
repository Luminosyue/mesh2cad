import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.74983, 0.30352, 0.07041), normal=(0.8984, -0.43914, 0.00575), xDir=(-0.43915, -0.89841, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.4217, 0.18698)
loop_1 = loop_1.lineTo(0.42918, 0.15527)
loop_1 = loop_1.lineTo(0.42855, 0.12826)
loop_1 = loop_1.lineTo(0.42698, 0.1015)
loop_1 = loop_1.threePointArc((0.42608, 0.0737), (0.42475, 0.04765))
loop_1 = loop_1.lineTo(0.42401, 0.03034)
loop_1 = loop_1.threePointArc((0.4235, -0.00938), (0.42188, -0.04759))
loop_1 = loop_1.lineTo(0.42102, -0.06758)
loop_1 = loop_1.lineTo(0.41755, -0.09978)
loop_1 = loop_1.lineTo(0.42166, 0.18408)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_27_interval_0.stl')