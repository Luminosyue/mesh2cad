import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.76488, -0.43076, -0.01474), normal=(-0.89584, 0.44438, 0.00038), xDir=(0.44438, 0.89584, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.31806, 0.19079)
loop_1 = loop_1.lineTo(0.31772, -0.16877)
loop_1 = loop_1.lineTo(0.32578, -0.15657)
loop_1 = loop_1.threePointArc((0.32696, -0.13481), (0.3287, -0.11217))
loop_1 = loop_1.threePointArc((0.32965, -0.08656), (0.33054, -0.06406))
loop_1 = loop_1.threePointArc((0.32929, -0.03762), (0.3279, -0.01596))
loop_1 = loop_1.lineTo(0.32907, 0.03542)
loop_1 = loop_1.lineTo(0.32853, 0.09029)
loop_1 = loop_1.lineTo(0.32797, 0.13531)
loop_1 = loop_1.threePointArc((0.32758, 0.15724), (0.32757, 0.17647))
loop_1 = loop_1.lineTo(0.31886, 0.18958)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_14_interval_0.stl')