import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.28483), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04298, 0.56087)
loop_1 = loop_1.threePointArc((-0.05095, 0.50945), (-0.06048, 0.45609))
loop_1 = loop_1.threePointArc((-0.0659, 0.42029), (-0.07012, 0.38626))
loop_1 = loop_1.threePointArc((-0.07733, 0.3477), (-0.0831, 0.31099))
loop_1 = loop_1.lineTo(-0.09708, 0.23843)
loop_1 = loop_1.threePointArc((-0.10303, 0.21049), (-0.10712, 0.18385))
loop_1 = loop_1.lineTo(-0.11, 0.16847)
loop_1 = loop_1.lineTo(-0.10876, 0.84276)
loop_1 = loop_1.lineTo(-0.04459, 0.58031)
loop_1 = loop_1.lineTo(-0.04298, 0.56087)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_55_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_55_interval_1.stl')