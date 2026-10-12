import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.5), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.68734, 0.85301)
loop_1 = loop_1.lineTo(0.62261, 0.85402)
loop_1 = loop_1.lineTo(0.35718, 0.85489)
loop_1 = loop_1.threePointArc((0.26959, 0.85572), (0.18636, 0.85491))
loop_1 = loop_1.threePointArc((-0.04074, 0.85664), (-0.2579, 0.85603))
loop_1 = loop_1.threePointArc((-0.37788, 0.85756), (-0.49219, 0.85612))
loop_1 = loop_1.threePointArc((-0.54785, 0.85688), (-0.60487, 0.85873))
loop_1 = loop_1.lineTo(-0.66038, 0.85688)
loop_1 = loop_1.lineTo(-0.68644, 0.85314)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_68_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_68_interval_1.stl')