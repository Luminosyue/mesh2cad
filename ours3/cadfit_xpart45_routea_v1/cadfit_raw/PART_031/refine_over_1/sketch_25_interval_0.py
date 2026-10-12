import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.07581, 0.74261, 0.03258), normal=(0.00656, -0.99998, -0.00062), xDir=(-0.99998, -0.00656, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.38763, 0.57627)
loop_1 = loop_1.lineTo(0.6018, 0.57406)
loop_1 = loop_1.lineTo(0.6018, 0.20681)
loop_1 = loop_1.lineTo(0.40043, 0.20374)
loop_1 = loop_1.lineTo(0.4158, 0.22102)
loop_1 = loop_1.lineTo(0.41986, 0.25455)
loop_1 = loop_1.lineTo(0.42036, 0.2711)
loop_1 = loop_1.lineTo(0.42541, 0.30989)
loop_1 = loop_1.lineTo(0.42407, 0.32061)
loop_1 = loop_1.lineTo(0.43613, 0.36492)
loop_1 = loop_1.lineTo(0.44809, 0.4202)
loop_1 = loop_1.lineTo(0.44918, 0.43917)
loop_1 = loop_1.lineTo(0.45041, 0.47)
loop_1 = loop_1.threePointArc((0.44888, 0.49875), (0.44753, 0.51979))
loop_1 = loop_1.lineTo(0.43613, 0.56444)
loop_1 = loop_1.lineTo(0.39199, 0.57525)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_25_interval_0.stl')