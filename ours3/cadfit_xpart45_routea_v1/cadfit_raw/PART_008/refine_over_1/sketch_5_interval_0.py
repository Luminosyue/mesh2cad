import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05637, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.68945, 0.34178)
loop_1 = loop_1.lineTo(0.68989, 0.29988)
loop_1 = loop_1.lineTo(0.6707, 0.30603)
loop_1 = loop_1.lineTo(0.63878, 0.30771)
loop_1 = loop_1.lineTo(0.61806, 0.3126)
loop_1 = loop_1.lineTo(0.40253, 0.31226)
loop_1 = loop_1.lineTo(0.05439, 0.31271)
loop_1 = loop_1.threePointArc((-0.00684, 0.31339), (-0.06468, 0.31303))
loop_1 = loop_1.lineTo(-0.31723, 0.31391)
loop_1 = loop_1.threePointArc((-0.44912, 0.31365), (-0.58547, 0.31501))
loop_1 = loop_1.lineTo(-0.62526, 0.31371)
loop_1 = loop_1.threePointArc((-0.65269, 0.30707), (-0.67769, 0.29936))
loop_1 = loop_1.threePointArc((-0.68935, 0.29158), (-0.6995, 0.2844))
loop_1 = loop_1.lineTo(-0.70021, 0.33356)
loop_1 = loop_1.lineTo(0.68852, 0.34177)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.84)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_5_interval_0.stl')