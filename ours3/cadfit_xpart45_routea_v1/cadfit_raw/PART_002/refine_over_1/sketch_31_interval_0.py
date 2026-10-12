import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00512, -0.59519, 0.05805), normal=(0.00015, 0.58735, -0.80933), xDir=(1.0, -0.00026, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.04782, -0.23952)
loop_1 = loop_1.lineTo(0.06029, -0.24017)
loop_1 = loop_1.lineTo(0.08348, -0.2372)
loop_1 = loop_1.lineTo(0.09535, -0.23532)
loop_1 = loop_1.lineTo(0.25465, -0.23537)
loop_1 = loop_1.lineTo(0.25467, -0.1664)
loop_1 = loop_1.lineTo(0.2427, -0.17025)
loop_1 = loop_1.lineTo(0.22654, -0.17393)
loop_1 = loop_1.lineTo(0.20837, -0.18368)
loop_1 = loop_1.lineTo(0.17673, -0.19921)
loop_1 = loop_1.lineTo(0.14882, -0.21329)
loop_1 = loop_1.lineTo(0.13141, -0.22101)
loop_1 = loop_1.threePointArc((0.12337, -0.22436), (0.115, -0.22785))
loop_1 = loop_1.lineTo(0.00126, -0.23632)
loop_1 = loop_1.lineTo(0.02595, -0.23845)
loop_1 = loop_1.lineTo(0.04503, -0.23939)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_31_interval_0.stl')