import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.48361, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.98828, -0.15149)
loop_1 = loop_1.lineTo(-0.98774, 0.11121)
loop_1 = loop_1.lineTo(-0.92431, -0.00878)
loop_1 = loop_1.threePointArc((-0.92741, -0.03405), (-0.93079, -0.06015))
loop_1 = loop_1.lineTo(-0.94408, -0.06813)
loop_1 = loop_1.threePointArc((-0.96295, -0.0889), (-0.98264, -0.11024))
loop_1 = loop_1.lineTo(-0.98802, -0.14993)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.88)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_73_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_73_interval_0.stl')