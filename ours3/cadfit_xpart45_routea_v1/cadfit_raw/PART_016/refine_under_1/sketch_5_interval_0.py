import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05833, 0.75186, -0.0486), normal=(-0.00029, -0.99999, -0.0052), xDir=(-1.0, 0.00029, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00463, 0.26197)
loop_1 = loop_1.threePointArc((0.0474, 0.2617), (0.09193, 0.26034))
loop_1 = loop_1.lineTo(0.12577, 0.25805)
loop_1 = loop_1.threePointArc((0.14663, 0.25693), (0.16366, 0.25613))
loop_1 = loop_1.lineTo(0.17488, 0.25461)
loop_1 = loop_1.lineTo(0.19317, 0.25217)
loop_1 = loop_1.lineTo(0.21661, 0.25043)
loop_1 = loop_1.lineTo(-0.24248, 0.24918)
loop_1 = loop_1.lineTo(-0.21609, 0.25517)
loop_1 = loop_1.lineTo(-0.17196, 0.25999)
loop_1 = loop_1.lineTo(-0.13647, 0.25979)
loop_1 = loop_1.lineTo(-0.12494, 0.26021)
loop_1 = loop_1.lineTo(-0.08176, 0.26012)
loop_1 = loop_1.threePointArc((-0.03885, 0.26132), (0.00074, 0.26195))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.63)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_5_interval_0.stl')