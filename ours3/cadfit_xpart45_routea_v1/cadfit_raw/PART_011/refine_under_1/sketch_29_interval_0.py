import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.8099, 0.1325, 0.00696), normal=(-0.97687, -0.21308, -0.01812), xDir=(-0.21311, 0.97703, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.41718, 0.1902)
loop_1 = loop_1.threePointArc((0.42011, 0.16964), (0.42297, 0.14991))
loop_1 = loop_1.lineTo(0.42233, 0.11428)
loop_1 = loop_1.lineTo(0.42307, 0.10179)
loop_1 = loop_1.threePointArc((0.42326, 0.07558), (0.4235, 0.05368))
loop_1 = loop_1.lineTo(0.42604, 0.01464)
loop_1 = loop_1.lineTo(0.42617, 0.00215)
loop_1 = loop_1.threePointArc((0.43052, -0.04328), (0.43436, -0.09066))
loop_1 = loop_1.lineTo(0.43567, -0.13877)
loop_1 = loop_1.lineTo(0.4173, 0.18683)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_29_interval_0.stl')