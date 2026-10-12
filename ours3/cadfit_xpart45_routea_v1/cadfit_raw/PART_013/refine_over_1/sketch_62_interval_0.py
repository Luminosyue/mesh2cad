import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.22347), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.82257, 0.51705)
loop_1 = loop_1.lineTo(-0.99663, 0.10031)
loop_1 = loop_1.threePointArc((-0.99462, 0.11751), (-0.99153, 0.13495))
loop_1 = loop_1.threePointArc((-0.98822, 0.15359), (-0.98391, 0.17252))
loop_1 = loop_1.threePointArc((-0.98029, 0.18815), (-0.97588, 0.20393))
loop_1 = loop_1.threePointArc((-0.97141, 0.2199), (-0.96611, 0.236))
loop_1 = loop_1.threePointArc((-0.96098, 0.25155), (-0.95501, 0.26719))
loop_1 = loop_1.lineTo(-0.93598, 0.31951)
loop_1 = loop_1.lineTo(-0.92084, 0.35577)
loop_1 = loop_1.lineTo(-0.90384, 0.39181)
loop_1 = loop_1.lineTo(-0.88524, 0.42702)
loop_1 = loop_1.lineTo(-0.86634, 0.45912)
loop_1 = loop_1.threePointArc((-0.85471, 0.4752), (-0.8422, 0.49126))
loop_1 = loop_1.lineTo(-0.82275, 0.51681)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_62_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_62_interval_0.stl')