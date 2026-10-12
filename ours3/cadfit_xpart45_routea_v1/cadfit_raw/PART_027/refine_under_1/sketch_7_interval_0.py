import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03395, 0.37165, -0.23901), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.03725, -0.37673)
loop_1 = loop_1.lineTo(-0.03401, -0.3936)
loop_1 = loop_1.lineTo(-0.01448, -0.39379)
loop_1 = loop_1.lineTo(-0.00453, -0.37597)
loop_1 = loop_1.lineTo(0.00505, -0.35756)
loop_1 = loop_1.lineTo(0.0055, -0.34443)
loop_1 = loop_1.lineTo(-0.00225, -0.33254)
loop_1 = loop_1.lineTo(-0.01448, -0.33376)
loop_1 = loop_1.lineTo(-0.03072, -0.35391)
loop_1 = loop_1.lineTo(-0.0348, -0.36437)
loop_1 = loop_1.lineTo(-0.03708, -0.37591)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_7_interval_0.stl')