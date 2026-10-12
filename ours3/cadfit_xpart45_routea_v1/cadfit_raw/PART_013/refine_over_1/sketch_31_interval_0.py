import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05296, -0.17162, 0.20155), normal=(7e-05, -0.10041, -0.99495), xDir=(0.0, -0.99495, 0.10041))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.69606, 0.34566)
loop_1 = loop_1.lineTo(0.70215, 0.33401)
loop_1 = loop_1.lineTo(0.7196, 0.29644)
loop_1 = loop_1.lineTo(0.73414, 0.26115)
loop_1 = loop_1.threePointArc((0.74729, 0.22476), (0.75934, 0.19242))
loop_1 = loop_1.lineTo(0.77007, 0.15863)
loop_1 = loop_1.lineTo(0.77826, 0.12835)
loop_1 = loop_1.lineTo(0.78586, 0.0936)
loop_1 = loop_1.lineTo(0.78856, 0.078)
loop_1 = loop_1.lineTo(0.78603, 0.08998)
loop_1 = loop_1.lineTo(0.7784, 0.11338)
loop_1 = loop_1.lineTo(0.77156, 0.13669)
loop_1 = loop_1.threePointArc((0.76244, 0.16348), (0.75424, 0.18641))
loop_1 = loop_1.threePointArc((0.74588, 0.21158), (0.73834, 0.23266))
loop_1 = loop_1.threePointArc((0.72583, 0.26931), (0.71341, 0.30159))
loop_1 = loop_1.lineTo(0.70477, 0.32484)
loop_1 = loop_1.lineTo(0.69735, 0.34254)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_31_interval_0.stl')