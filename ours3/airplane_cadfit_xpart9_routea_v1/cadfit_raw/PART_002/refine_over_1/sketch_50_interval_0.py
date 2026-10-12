import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.02448), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.14141, 0.82511)
loop_1 = loop_1.lineTo(0.14815, 0.80158)
loop_1 = loop_1.lineTo(0.15402, 0.76794)
loop_1 = loop_1.lineTo(0.15502, 0.7291)
loop_1 = loop_1.threePointArc((0.15379, 0.71227), (0.15217, 0.69509))
loop_1 = loop_1.threePointArc((0.15043, 0.67921), (0.14951, 0.66418))
loop_1 = loop_1.threePointArc((0.14702, 0.63763), (0.14341, 0.6104))
loop_1 = loop_1.lineTo(0.13917, 0.57157)
loop_1 = loop_1.threePointArc((0.13701, 0.5497), (0.13445, 0.52726))
loop_1 = loop_1.lineTo(0.13419, 0.45048)
loop_1 = loop_1.threePointArc((0.12548, 0.45642), (0.12573, 0.46188))
loop_1 = loop_1.lineTo(0.0908, 0.85578)
loop_1 = loop_1.lineTo(0.11068, 0.85658)
loop_1 = loop_1.lineTo(0.12355, 0.85366)
loop_1 = loop_1.lineTo(0.13626, 0.83531)
loop_1 = loop_1.lineTo(0.14141, 0.82511)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_50_interval_0.stl')