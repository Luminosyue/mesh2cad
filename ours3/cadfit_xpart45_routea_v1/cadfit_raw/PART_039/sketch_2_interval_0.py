import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.87784, -0.07249, 0.00402), normal=(0.0566, 0.99789, 0.03193), xDir=(0.9984, -0.05662, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02851, 0.09955)
loop_1 = loop_1.lineTo(0.01139, 0.08854)
loop_1 = loop_1.lineTo(-0.01097, 0.07019)
loop_1 = loop_1.lineTo(-0.01928, 0.05462)
loop_1 = loop_1.lineTo(-0.01731, 0.04403)
loop_1 = loop_1.lineTo(-0.01135, 0.03354)
loop_1 = loop_1.threePointArc((0.00126, 0.02552), (0.01344, 0.01793))
loop_1 = loop_1.lineTo(0.00501, -0.00418)
loop_1 = loop_1.lineTo(0.0077, -0.02819)
loop_1 = loop_1.lineTo(0.0003, -0.04251)
loop_1 = loop_1.lineTo(0.02293, -0.08511)
loop_1 = loop_1.threePointArc((0.02905, -0.08811), (0.03497, -0.09089))
loop_1 = loop_1.lineTo(0.08798, -0.01932)
loop_1 = loop_1.threePointArc((0.08684, 0.00222), (0.08585, 0.02467))
loop_1 = loop_1.lineTo(0.07488, 0.09434)
loop_1 = loop_1.lineTo(0.06177, 0.09939)
loop_1 = loop_1.lineTo(0.02851, 0.09955)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_039/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_039/sketch_2_interval_0.stl')