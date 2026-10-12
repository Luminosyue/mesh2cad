import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.17, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.2845, 0.00556)
loop_1 = loop_1.lineTo(-0.3032, 0.00227)
loop_1 = loop_1.threePointArc((-0.31148, 0.00069), (-0.31923, -0.00112))
loop_1 = loop_1.lineTo(-0.33776, -0.00595)
loop_1 = loop_1.lineTo(-0.35121, -0.00847)
loop_1 = loop_1.threePointArc((-0.36918, -0.01138), (-0.3878, -0.01415))
loop_1 = loop_1.threePointArc((-0.39459, -0.01469), (-0.40094, -0.01541))
loop_1 = loop_1.lineTo(-0.41189, -0.01711)
loop_1 = loop_1.threePointArc((-0.42536, -0.02063), (-0.43524, -0.02387))
loop_1 = loop_1.lineTo(-0.23119, -0.00844)
loop_1 = loop_1.lineTo(-0.24055, 0.00179)
loop_1 = loop_1.threePointArc((-0.24814, 0.00383), (-0.25548, 0.00558))
loop_1 = loop_1.threePointArc((-0.26216, 0.00606), (-0.26844, 0.00607))
loop_1 = loop_1.lineTo(-0.2845, 0.00556)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_52_interval_0.stl')