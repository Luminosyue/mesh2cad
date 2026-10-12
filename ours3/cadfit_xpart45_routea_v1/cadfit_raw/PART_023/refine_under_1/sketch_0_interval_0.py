import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.49533, 0.40978, 0.03135), normal=(0.00466, -0.99999, 1e-05), xDir=(-0.99999, -0.00466, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10041, 1.00545)
loop_1 = loop_1.lineTo(0.10065, 0.86972)
loop_1 = loop_1.threePointArc((0.11382, 0.87736), (0.12517, 0.88394))
loop_1 = loop_1.lineTo(0.15112, 0.91516)
loop_1 = loop_1.lineTo(0.15325, 0.94098)
loop_1 = loop_1.lineTo(0.15131, 0.96766)
loop_1 = loop_1.lineTo(0.13778, 0.99202)
loop_1 = loop_1.lineTo(0.12513, 1.00056)
loop_1 = loop_1.lineTo(0.10191, 1.00516)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.68)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_0_interval_0.stl')