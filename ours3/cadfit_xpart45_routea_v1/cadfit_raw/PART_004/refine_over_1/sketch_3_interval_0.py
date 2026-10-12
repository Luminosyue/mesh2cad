import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.35391, -0.29211, -0.1686), normal=(0.62474, 0.78083, 0.00122), xDir=(0.78083, -0.62474, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0692, -0.56256)
loop_1 = loop_1.threePointArc((-0.06966, -0.57624), (-0.06995, -0.58937))
loop_1 = loop_1.lineTo(-0.07015, -0.57618)
loop_1 = loop_1.lineTo(-0.07134, 0.63141)
loop_1 = loop_1.lineTo(-0.06106, 0.63141)
loop_1 = loop_1.lineTo(-0.06928, -0.56238)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.06924, -0.56228)
loop_2 = loop_2.threePointArc((-0.06968, -0.5761), (-0.06995, -0.58937))
loop_2 = loop_2.lineTo(-0.07015, -0.57618)
loop_2 = loop_2.lineTo(-0.07134, 0.63141)
loop_2 = loop_2.lineTo(-0.06106, 0.63141)
loop_2 = loop_2.lineTo(-0.06919, -0.54958)
loop_2 = loop_2.lineTo(-0.06924, -0.56228)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_3_interval_0.stl')