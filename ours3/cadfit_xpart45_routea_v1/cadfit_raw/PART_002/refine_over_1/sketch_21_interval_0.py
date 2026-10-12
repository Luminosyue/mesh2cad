import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01999, 0.27494, 0.65124), normal=(7e-05, 0.78371, 0.62113), xDir=(1.0, -9e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26691, -0.13825)
loop_1 = loop_1.lineTo(-0.26593, -0.15445)
loop_1 = loop_1.lineTo(-0.25682, -0.18549)
loop_1 = loop_1.lineTo(-0.24613, -0.19465)
loop_1 = loop_1.lineTo(-0.45536, -0.19465)
loop_1 = loop_1.lineTo(-0.41952, -0.13799)
loop_1 = loop_1.lineTo(-0.38285, -0.0846)
loop_1 = loop_1.lineTo(-0.34915, -0.03899)
loop_1 = loop_1.lineTo(-0.33698, -0.02076)
loop_1 = loop_1.lineTo(-0.32881, -0.01069)
loop_1 = loop_1.lineTo(-0.26184, 0.04797)
loop_1 = loop_1.lineTo(-0.22939, 0.06418)
loop_1 = loop_1.lineTo(-0.19251, 0.07998)
loop_1 = loop_1.lineTo(-0.15385, 0.09367)
loop_1 = loop_1.lineTo(-0.26465, -0.13392)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_21_interval_0.stl')