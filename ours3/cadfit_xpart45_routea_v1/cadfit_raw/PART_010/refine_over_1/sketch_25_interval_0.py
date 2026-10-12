import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.5768, 0.04792, 0.3356), normal=(-0.79983, -0.01226, 0.6001), xDir=(-0.01533, 0.99988, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.07915, -0.26978)
loop_1 = loop_1.lineTo(0.0787, -0.31921)
loop_1 = loop_1.lineTo(0.19831, -0.31965)
loop_1 = loop_1.lineTo(0.16687, -0.31057)
loop_1 = loop_1.lineTo(0.14583, -0.2988)
loop_1 = loop_1.lineTo(0.13487, -0.29142)
loop_1 = loop_1.lineTo(0.11345, -0.28257)
loop_1 = loop_1.lineTo(0.09435, -0.27202)
loop_1 = loop_1.lineTo(0.07999, -0.26987)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_25_interval_0.stl')