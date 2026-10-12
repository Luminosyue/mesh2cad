import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.57603, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.80604, -0.08771)
loop_1 = loop_1.lineTo(0.80555, 0.05524)
loop_1 = loop_1.lineTo(0.7892, 0.03677)
loop_1 = loop_1.lineTo(0.77495, 0.02217)
loop_1 = loop_1.lineTo(0.74431, -0.00257)
loop_1 = loop_1.lineTo(0.74871, -0.04175)
loop_1 = loop_1.lineTo(0.75192, -0.05447)
loop_1 = loop_1.lineTo(0.77601, -0.06162)
loop_1 = loop_1.lineTo(0.80604, -0.0877)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_68_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_68_interval_0.stl')