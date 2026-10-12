import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.77303), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30946, 0.25)
loop_1 = loop_1.lineTo(0.35276, 0.24981)
loop_1 = loop_1.lineTo(0.35252, 0.00274)
loop_1 = loop_1.threePointArc((0.35218, 0.01125), (0.35154, 0.01922))
loop_1 = loop_1.lineTo(0.35065, 0.048)
loop_1 = loop_1.threePointArc((0.34919, 0.06522), (0.34798, 0.08299))
loop_1 = loop_1.threePointArc((0.34715, 0.0886), (0.34629, 0.09379))
loop_1 = loop_1.lineTo(0.32276, 0.19884)
loop_1 = loop_1.lineTo(0.31048, 0.24758)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.58)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_96_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_96_interval_0.stl')