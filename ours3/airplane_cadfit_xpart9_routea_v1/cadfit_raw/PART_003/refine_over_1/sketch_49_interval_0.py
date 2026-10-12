import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.1187, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17256, 0.27126)
loop_1 = loop_1.threePointArc((0.20453, 0.27918), (0.23495, 0.28779))
loop_1 = loop_1.threePointArc((0.19974, 0.28898), (0.16137, 0.2931))
loop_1 = loop_1.lineTo(0.11279, 0.29746)
loop_1 = loop_1.lineTo(0.07135, 0.29781)
loop_1 = loop_1.lineTo(-0.6561, 0.05991)
loop_1 = loop_1.lineTo(-0.58529, 0.07627)
loop_1 = loop_1.lineTo(-0.52216, 0.09145)
loop_1 = loop_1.lineTo(-0.4542, 0.1104)
loop_1 = loop_1.threePointArc((-0.42254, 0.11756), (-0.39324, 0.12625))
loop_1 = loop_1.lineTo(-0.34504, 0.14108)
loop_1 = loop_1.threePointArc((-0.31458, 0.14928), (-0.28645, 0.15881))
loop_1 = loop_1.threePointArc((-0.20589, 0.18171), (-0.12145, 0.20081))
loop_1 = loop_1.threePointArc((-0.06802, 0.21231), (-0.01748, 0.22385))
loop_1 = loop_1.threePointArc((0.02969, 0.23559), (0.07414, 0.2476))
loop_1 = loop_1.threePointArc((0.12264, 0.25832), (0.16816, 0.27024))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_49_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_49_interval_0.stl')