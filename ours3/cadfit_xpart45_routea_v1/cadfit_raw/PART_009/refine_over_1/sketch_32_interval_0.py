import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.8569, 0.36294, 0.16743), normal=(-0.91532, 0.40273, -0.0), xDir=(0.40273, 0.91532, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28937, 0.68764)
loop_1 = loop_1.lineTo(0.34435, 0.68764)
loop_1 = loop_1.lineTo(0.34435, 0.49835)
loop_1 = loop_1.threePointArc((0.34098, 0.53558), (0.33756, 0.56908))
loop_1 = loop_1.lineTo(0.336, 0.58305)
loop_1 = loop_1.threePointArc((0.33187, 0.60852), (0.32764, 0.63293))
loop_1 = loop_1.lineTo(0.31332, 0.65797)
loop_1 = loop_1.lineTo(0.29406, 0.68492)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_32_interval_0.stl')