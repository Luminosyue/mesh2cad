import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.22523), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.56414, 0.48864)
loop_1 = loop_1.lineTo(-0.44755, 0.37994)
loop_1 = loop_1.lineTo(-0.33761, 0.26772)
loop_1 = loop_1.lineTo(-0.3575, 0.24776)
loop_1 = loop_1.threePointArc((-0.36225, 0.25238), (-0.37415, 0.26581))
loop_1 = loop_1.threePointArc((-0.39401, 0.28915), (-0.41339, 0.31097))
loop_1 = loop_1.threePointArc((-0.4274, 0.3273), (-0.4416, 0.3443))
loop_1 = loop_1.threePointArc((-0.45443, 0.36072), (-0.46699, 0.37596))
loop_1 = loop_1.lineTo(-0.49493, 0.40733)
loop_1 = loop_1.threePointArc((-0.51058, 0.42549), (-0.52627, 0.44459))
loop_1 = loop_1.threePointArc((-0.53322, 0.45331), (-0.54061, 0.4614))
loop_1 = loop_1.threePointArc((-0.55216, 0.47473), (-0.56394, 0.48848))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.84)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_53_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_53_interval_0.stl')