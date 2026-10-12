import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.39722, -0.0802, -0.1647), normal=(0.01135, 0.95015, -0.31158), xDir=(0.99993, -0.01194, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.31136, -0.38352)
loop_1 = loop_1.lineTo(-1.30261, -0.36251)
loop_1 = loop_1.threePointArc((-1.28789, -0.3558), (-1.27747, -0.35175))
loop_1 = loop_1.lineTo(-1.269, -0.33897)
loop_1 = loop_1.lineTo(-1.25339, -0.32403)
loop_1 = loop_1.lineTo(-1.24286, -0.31749)
loop_1 = loop_1.lineTo(-1.23536, -0.30382)
loop_1 = loop_1.lineTo(-1.22375, -0.28876)
loop_1 = loop_1.lineTo(-1.21041, -0.28096)
loop_1 = loop_1.lineTo(-1.19073, -0.26635)
loop_1 = loop_1.lineTo(-1.33592, -0.255)
loop_1 = loop_1.lineTo(-1.31257, -0.38427)
loop_1 = loop_1.lineTo(-1.32631, -0.39276)
loop_1 = loop_1.lineTo(-1.31136, -0.38352)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_25_interval_0.stl')