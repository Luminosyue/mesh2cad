import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.83213, -0.25869, -0.02713), normal=(-0.96225, 0.27216, 0.00118), xDir=(0.27216, 0.96225, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34039, -0.20124)
loop_1 = loop_1.lineTo(0.30075, -0.20124)
loop_1 = loop_1.lineTo(0.31741, 0.20876)
loop_1 = loop_1.lineTo(-0.31974, 0.20876)
loop_1 = loop_1.lineTo(-0.33986, -0.19069)
loop_1 = loop_1.lineTo(-0.34039, -0.20124)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.72)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_32_interval_0.stl')