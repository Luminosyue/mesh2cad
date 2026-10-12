import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.68861, 0.05075, 0.07081), normal=(-1.0, -0.0, 0.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.13568, 0.27199)
loop_1 = loop_1.lineTo(0.55943, 0.24946)
loop_1 = loop_1.lineTo(0.54199, -0.18919)
loop_1 = loop_1.lineTo(-0.80109, -0.18919)
loop_1 = loop_1.lineTo(-0.78931, 0.27262)
loop_1 = loop_1.lineTo(-0.71253, 0.27255)
loop_1 = loop_1.lineTo(-0.69569, 0.27253)
loop_1 = loop_1.lineTo(-0.45247, 0.27229)
loop_1 = loop_1.lineTo(-0.44, 0.27228)
loop_1 = loop_1.lineTo(-0.15421, 0.272)
loop_1 = loop_1.lineTo(-0.13568, 0.27199)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_21_interval_0.stl')