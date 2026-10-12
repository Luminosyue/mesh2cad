import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.13069, -0.93026, 0.04684), normal=(-0.14078, 0.98944, 0.0345), xDir=(0.99003, 0.14087, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08269, 0.28562)
loop_1 = loop_1.lineTo(-0.14546, 0.28437)
loop_1 = loop_1.threePointArc((-0.17229, 0.28274), (-0.19473, 0.28104))
loop_1 = loop_1.lineTo(0.14595, 0.27737)
loop_1 = loop_1.lineTo(0.11641, 0.28034)
loop_1 = loop_1.lineTo(0.10176, 0.28274)
loop_1 = loop_1.lineTo(0.06664, 0.28314)
loop_1 = loop_1.lineTo(0.04029, 0.28199)
loop_1 = loop_1.lineTo(0.01687, 0.28406)
loop_1 = loop_1.lineTo(-0.00333, 0.28348)
loop_1 = loop_1.lineTo(-0.03291, 0.28521)
loop_1 = loop_1.lineTo(-0.04695, 0.28487)
loop_1 = loop_1.lineTo(-0.07912, 0.28554)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.88)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_37_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_37_interval_0.stl')