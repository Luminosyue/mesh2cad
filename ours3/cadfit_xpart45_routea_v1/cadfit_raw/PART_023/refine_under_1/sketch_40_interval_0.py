import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.69857, -0.77763, -0.073), normal=(0.91096, 0.4125, -4e-05), xDir=(0.4125, -0.91096, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.09544, -0.73652)
loop_1 = loop_1.lineTo(0.1254, -0.74172)
loop_1 = loop_1.lineTo(0.1465, -0.76595)
loop_1 = loop_1.lineTo(0.1498, -0.79637)
loop_1 = loop_1.lineTo(0.14299, -0.80903)
loop_1 = loop_1.lineTo(0.13242, -0.82247)
loop_1 = loop_1.lineTo(0.11496, -0.82883)
loop_1 = loop_1.lineTo(0.0944, -0.83351)
loop_1 = loop_1.lineTo(0.07412, -0.82826)
loop_1 = loop_1.lineTo(0.05328, -0.79542)
loop_1 = loop_1.lineTo(0.05305, -0.77003)
loop_1 = loop_1.lineTo(0.06325, -0.75523)
loop_1 = loop_1.lineTo(0.07191, -0.74465)
loop_1 = loop_1.lineTo(0.09402, -0.73698)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.68)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_40_interval_0.stl')