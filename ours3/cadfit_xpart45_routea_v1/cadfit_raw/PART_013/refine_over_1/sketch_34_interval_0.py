import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.76833, 0.22528, 0.01193), normal=(0.9252, -0.37895, 0.01983), xDir=(-0.37903, -0.92538, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.33726, 0.15677)
loop_1 = loop_1.lineTo(0.32908, 0.00087)
loop_1 = loop_1.threePointArc((0.32833, 0.02007), (0.32785, 0.03818))
loop_1 = loop_1.lineTo(0.32899, 0.10751)
loop_1 = loop_1.lineTo(0.32817, 0.118)
loop_1 = loop_1.threePointArc((0.31919, 0.13258), (0.31056, 0.14657))
loop_1 = loop_1.lineTo(0.33593, 0.15677)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_34_interval_0.stl')