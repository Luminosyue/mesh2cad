import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02464, -0.94184, 0.09644), normal=(-7e-05, 0.99999, -0.00529), xDir=(1.0, 7e-05, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28399, -0.16367)
loop_1 = loop_1.lineTo(0.37002, -0.16367)
loop_1 = loop_1.lineTo(0.36556, -0.0931)
loop_1 = loop_1.lineTo(0.31698, 0.23389)
loop_1 = loop_1.lineTo(0.31545, 0.24634)
loop_1 = loop_1.lineTo(-0.24754, 0.24634)
loop_1 = loop_1.lineTo(-0.27673, -0.09644)
loop_1 = loop_1.lineTo(-0.28364, -0.16043)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.83)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_19_interval_0.stl')