import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.11862, 0.31731, 0.12721), normal=(0.00749, 0.99997, 0.00163), xDir=(0.99997, -0.00749, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.24392, 0.75161)
loop_1 = loop_1.lineTo(-0.27507, 0.74985)
loop_1 = loop_1.lineTo(-0.30655, 0.74674)
loop_1 = loop_1.lineTo(-0.33851, 0.74218)
loop_1 = loop_1.lineTo(-0.35237, 0.73921)
loop_1 = loop_1.threePointArc((-0.32058, 0.74043), (-0.29006, 0.7409))
loop_1 = loop_1.lineTo(-0.27431, 0.74143)
loop_1 = loop_1.threePointArc((-0.2573, 0.74236), (-0.24097, 0.74334))
loop_1 = loop_1.lineTo(-0.22707, 0.74285)
loop_1 = loop_1.lineTo(-0.20083, 0.74305)
loop_1 = loop_1.lineTo(-0.14312, 0.73901)
loop_1 = loop_1.threePointArc((-0.11858, 0.73771), (-0.09624, 0.73593))
loop_1 = loop_1.threePointArc((-0.07791, 0.73454), (-0.06215, 0.73297))
loop_1 = loop_1.lineTo(-0.04031, 0.73004)
loop_1 = loop_1.lineTo(-0.06987, 0.73618)
loop_1 = loop_1.lineTo(-0.13543, 0.74307)
loop_1 = loop_1.threePointArc((-0.18884, 0.74789), (-0.23715, 0.7516))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.65)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_30_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_30_interval_1.stl')