import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.1575, -0.04487, 0.4215), normal=(0.81097, 0.00031, 0.58509), xDir=(0.00039, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.84612, 0.64876)
loop_1 = loop_1.lineTo(-0.85637, 0.62444)
loop_1 = loop_1.lineTo(-0.88401, 0.55249)
loop_1 = loop_1.lineTo(-0.90973, 0.47826)
loop_1 = loop_1.lineTo(-0.93202, 0.40675)
loop_1 = loop_1.lineTo(-0.91624, 0.42305)
loop_1 = loop_1.lineTo(-0.8784, 0.44992)
loop_1 = loop_1.lineTo(-0.86183, 0.45734)
loop_1 = loop_1.threePointArc((-0.84387, 0.48076), (-0.82815, 0.50382))
loop_1 = loop_1.lineTo(-0.8176, 0.52233)
loop_1 = loop_1.lineTo(-0.83267, 0.55031)
loop_1 = loop_1.lineTo(-0.83899, 0.56144)
loop_1 = loop_1.lineTo(-0.84945, 0.58296)
loop_1 = loop_1.threePointArc((-0.84815, 0.61803), (-0.84612, 0.64855))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_43_interval_0.stl')