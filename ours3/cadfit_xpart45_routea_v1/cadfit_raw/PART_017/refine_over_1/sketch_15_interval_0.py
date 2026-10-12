import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.12534, -0.39605, 0.04967), normal=(0.00148, 1.0, -0.00071), xDir=(1.0, -0.00148, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.92991, 0.4295)
loop_1 = loop_1.lineTo(-0.94094, 0.39789)
loop_1 = loop_1.threePointArc((-0.94638, 0.38178), (-0.95046, 0.36962))
loop_1 = loop_1.lineTo(-0.90739, 0.5216)
loop_1 = loop_1.lineTo(-0.97208, 0.5216)
loop_1 = loop_1.lineTo(-0.9722, 0.29894)
loop_1 = loop_1.lineTo(-0.96855, 0.31024)
loop_1 = loop_1.threePointArc((-0.96431, 0.32495), (-0.96113, 0.33611))
loop_1 = loop_1.lineTo(-0.93066, 0.42731)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.51)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_15_interval_0.stl')