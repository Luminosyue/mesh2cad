import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.44755, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.5897, -0.61075)
loop_1 = loop_1.lineTo(-0.46862, -0.61279)
loop_1 = loop_1.threePointArc((-0.4048, -0.61359), (-0.33865, -0.61518))
loop_1 = loop_1.lineTo(-0.30736, -0.61299)
loop_1 = loop_1.lineTo(-0.27286, -0.60606)
loop_1 = loop_1.lineTo(-0.23811, -0.59212)
loop_1 = loop_1.lineTo(-0.23747, -0.4035)
loop_1 = loop_1.lineTo(-0.23844, -0.39215)
loop_1 = loop_1.lineTo(-0.5891, -0.61077)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_42_interval_0.stl')