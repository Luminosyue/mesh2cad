import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04389, -0.88685, 0.03484), normal=(-1e-05, 0.71702, 0.69705), xDir=(1.0, 1e-05, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.44977, -0.08767)
loop_1 = loop_1.lineTo(0.45471, -0.15938)
loop_1 = loop_1.lineTo(0.46393, -0.1783)
loop_1 = loop_1.lineTo(0.46965, -0.19277)
loop_1 = loop_1.lineTo(0.49552, -0.20273)
loop_1 = loop_1.lineTo(0.50888, -0.2035)
loop_1 = loop_1.lineTo(-0.38378, -0.20613)
loop_1 = loop_1.lineTo(-0.35949, -0.19277)
loop_1 = loop_1.lineTo(-0.34501, -0.17829)
loop_1 = loop_1.lineTo(-0.33155, -0.14078)
loop_1 = loop_1.lineTo(0.45128, -0.13589)
loop_1 = loop_1.lineTo(0.44918, -0.12333)
loop_1 = loop_1.lineTo(0.44917, -0.10073)
loop_1 = loop_1.lineTo(0.44977, -0.08767)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_57_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_57_interval_0.stl')