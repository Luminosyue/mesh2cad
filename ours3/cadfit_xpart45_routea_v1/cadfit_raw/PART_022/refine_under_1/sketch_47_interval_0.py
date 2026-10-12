import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.74671, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.90797, -0.30115)
loop_1 = loop_1.lineTo(0.88536, -0.31852)
loop_1 = loop_1.threePointArc((0.88038, -0.32567), (0.87412, -0.3304))
loop_1 = loop_1.threePointArc((0.85374, -0.34839), (0.83236, -0.36483))
loop_1 = loop_1.threePointArc((0.71845, -0.36892), (0.60109, -0.36897))
loop_1 = loop_1.lineTo(0.30295, -0.36761)
loop_1 = loop_1.lineTo(0.1768, -0.36628)
loop_1 = loop_1.threePointArc((0.04019, -0.36759), (-0.10085, -0.36628))
loop_1 = loop_1.lineTo(-0.23679, -0.36579)
loop_1 = loop_1.lineTo(-0.43515, -0.36505)
loop_1 = loop_1.threePointArc((-0.53874, -0.36493), (-0.64538, -0.36312))
loop_1 = loop_1.threePointArc((-0.74371, -0.36176), (-0.84468, -0.35558))
loop_1 = loop_1.lineTo(-0.89324, -0.32438)
loop_1 = loop_1.threePointArc((-0.901, -0.31339), (-0.90719, -0.30224))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_47_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_47_interval_0.stl')