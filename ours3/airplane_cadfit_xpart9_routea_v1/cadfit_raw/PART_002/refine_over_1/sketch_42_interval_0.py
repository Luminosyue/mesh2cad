import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.02039, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.6501, -2e-05)
loop_1 = loop_1.threePointArc((-0.63918, -0.01067), (-0.62694, -0.0187))
loop_1 = loop_1.lineTo(-0.59932, -0.03655)
loop_1 = loop_1.lineTo(-0.56412, -0.05311)
loop_1 = loop_1.lineTo(-0.53267, -0.06501)
loop_1 = loop_1.lineTo(-0.4991, -0.0735)
loop_1 = loop_1.lineTo(-0.46456, -0.08634)
loop_1 = loop_1.threePointArc((-0.4292, -0.09714), (-0.39549, -0.10646))
loop_1 = loop_1.threePointArc((-0.36725, -0.11079), (-0.34044, -0.11307))
loop_1 = loop_1.lineTo(-0.29453, -0.11735)
loop_1 = loop_1.threePointArc((-0.26486, -0.11872), (-0.23464, -0.12182))
loop_1 = loop_1.lineTo(-0.15819, -0.1333)
loop_1 = loop_1.lineTo(-0.08761, -0.14685)
loop_1 = loop_1.threePointArc((-0.05973, -0.15253), (-0.03322, -0.15648))
loop_1 = loop_1.threePointArc((0.00437, -0.16381), (0.04013, -0.16966))
loop_1 = loop_1.lineTo(-0.65014, -0.16841)
loop_1 = loop_1.lineTo(-0.65014, -0.00058)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_42_interval_0.stl')