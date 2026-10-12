import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00087, 0.10923, 0.07146), normal=(-0.1889, -0.58283, -0.79033), xDir=(-0.95128, 0.30832, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.69501, 0.11613)
loop_1 = loop_1.threePointArc((-0.6758, 0.11128), (-0.65731, 0.1068))
loop_1 = loop_1.lineTo(-0.60241, 0.091)
loop_1 = loop_1.lineTo(-0.57247, 0.07425)
loop_1 = loop_1.lineTo(-0.53305, 0.05422)
loop_1 = loop_1.lineTo(-0.43004, 0.01168)
loop_1 = loop_1.lineTo(-0.40313, -0.00358)
loop_1 = loop_1.lineTo(-0.69211, 0.11493)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_21_interval_0.stl')