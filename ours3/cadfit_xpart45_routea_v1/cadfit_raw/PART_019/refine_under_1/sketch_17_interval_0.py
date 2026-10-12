import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.24424, 0.00207, 0.92082), normal=(-0.13998, -0.00471, -0.99014), xDir=(0.0, -0.99999, 0.00476))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.78388, -0.15159)
loop_1 = loop_1.lineTo(0.78387, 0.39443)
loop_1 = loop_1.lineTo(0.78893, 0.37424)
loop_1 = loop_1.threePointArc((0.79337, 0.34163), (0.79787, 0.31195))
loop_1 = loop_1.lineTo(0.81273, 0.17023)
loop_1 = loop_1.lineTo(0.81684, 0.12481)
loop_1 = loop_1.lineTo(0.81699, 0.11402)
loop_1 = loop_1.lineTo(0.81302, 0.06911)
loop_1 = loop_1.lineTo(0.8057, 0.01455)
loop_1 = loop_1.lineTo(0.80657, 0.00044)
loop_1 = loop_1.lineTo(0.80688, -0.01832)
loop_1 = loop_1.lineTo(0.79727, -0.06186)
loop_1 = loop_1.lineTo(0.79622, -0.09002)
loop_1 = loop_1.threePointArc((0.79016, -0.12102), (0.78585, -0.14487))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.87)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_17_interval_0.stl')