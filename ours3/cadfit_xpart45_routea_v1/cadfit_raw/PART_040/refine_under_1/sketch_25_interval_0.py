import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.32591, 0.35826)
loop_1 = loop_1.threePointArc((0.3269, 0.34945), (0.32805, 0.34102))
loop_1 = loop_1.lineTo(0.34099, 0.32367)
loop_1 = loop_1.threePointArc((0.34688, 0.32011), (0.35254, 0.31671))
loop_1 = loop_1.threePointArc((0.3614, 0.31402), (0.36871, 0.31196))
loop_1 = loop_1.lineTo(0.40714, 0.32595)
loop_1 = loop_1.lineTo(0.42385, 0.35959)
loop_1 = loop_1.threePointArc((0.42209, 0.36709), (0.42032, 0.37493))
loop_1 = loop_1.lineTo(0.40079, 0.39577)
loop_1 = loop_1.threePointArc((0.39343, 0.39832), (0.38581, 0.40109))
loop_1 = loop_1.threePointArc((0.37654, 0.40067), (0.36895, 0.40024))
loop_1 = loop_1.lineTo(0.34507, 0.38898)
loop_1 = loop_1.lineTo(0.33061, 0.3735)
loop_1 = loop_1.threePointArc((0.32838, 0.36641), (0.32631, 0.35958))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_25_interval_0.stl')