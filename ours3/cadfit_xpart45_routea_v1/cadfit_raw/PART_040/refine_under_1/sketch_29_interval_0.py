import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.31462, -0.90149)
loop_1 = loop_1.lineTo(0.28461, -0.92132)
loop_1 = loop_1.threePointArc((0.27857, -0.92199), (0.27226, -0.92258))
loop_1 = loop_1.threePointArc((0.26049, -0.9218), (0.25273, -0.92061))
loop_1 = loop_1.threePointArc((0.2442, -0.91588), (0.23686, -0.91159))
loop_1 = loop_1.lineTo(0.22609, -0.89141)
loop_1 = loop_1.threePointArc((0.22556, -0.88362), (0.22493, -0.87616))
loop_1 = loop_1.threePointArc((0.22617, -0.867), (0.22701, -0.85952))
loop_1 = loop_1.threePointArc((0.23135, -0.85231), (0.23511, -0.84612))
loop_1 = loop_1.lineTo(0.25272, -0.83505)
loop_1 = loop_1.threePointArc((0.26156, -0.83343), (0.26936, -0.83223))
loop_1 = loop_1.lineTo(0.32003, -0.86118)
loop_1 = loop_1.lineTo(0.32141, -0.87467)
loop_1 = loop_1.lineTo(0.31462, -0.90149)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_29_interval_0.stl')