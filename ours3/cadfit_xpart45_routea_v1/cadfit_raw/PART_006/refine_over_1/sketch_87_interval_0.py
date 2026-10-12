import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.58029), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.33335, -0.9108)
loop_1 = loop_1.lineTo(0.25996, -0.93955)
loop_1 = loop_1.threePointArc((0.27111, -0.93667), (0.28146, -0.93374))
loop_1 = loop_1.threePointArc((0.30583, -0.92576), (0.32877, -0.91766))
loop_1 = loop_1.lineTo(0.38469, -0.89038)
loop_1 = loop_1.lineTo(0.38969, -0.99263)
loop_1 = loop_1.lineTo(0.07474, -0.99199)
loop_1 = loop_1.lineTo(0.33305, -0.9109)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_87_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_87_interval_0.stl')