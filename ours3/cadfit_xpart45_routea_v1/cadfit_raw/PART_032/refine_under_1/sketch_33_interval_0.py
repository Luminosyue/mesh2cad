import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02215, 0.11444, -0.28511), normal=(0.0003, -0.00064, 1.0), xDir=(-0.0, 1.0, 0.00064))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.82868, -0.23201)
loop_1 = loop_1.lineTo(-0.82509, -0.24414)
loop_1 = loop_1.lineTo(-0.81118, -0.2758)
loop_1 = loop_1.lineTo(-0.80259, -0.29103)
loop_1 = loop_1.lineTo(-0.79188, -0.31689)
loop_1 = loop_1.lineTo(-0.79284, -0.2964)
loop_1 = loop_1.lineTo(-0.80797, -0.25654)
loop_1 = loop_1.lineTo(-0.81286, -0.22786)
loop_1 = loop_1.lineTo(-0.8165, -0.19903)
loop_1 = loop_1.lineTo(-0.81889, -0.17014)
loop_1 = loop_1.lineTo(-0.82004, -0.14119)
loop_1 = loop_1.lineTo(-0.81996, -0.11461)
loop_1 = loop_1.lineTo(-0.82706, -0.13827)
loop_1 = loop_1.lineTo(-0.82951, -0.15038)
loop_1 = loop_1.lineTo(-0.83303, -0.18514)
loop_1 = loop_1.lineTo(-0.83229, -0.19726)
loop_1 = loop_1.lineTo(-0.82889, -0.22996)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.61)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_33_interval_0.stl')