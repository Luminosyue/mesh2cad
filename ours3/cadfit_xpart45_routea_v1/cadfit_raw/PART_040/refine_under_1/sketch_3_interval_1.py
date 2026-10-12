import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.80859, 0.20724, -0.02288), normal=(-0.67466, 0.73812, 0.0012), xDir=(0.73812, 0.67466, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05656, 0.02004)
loop_1 = loop_1.lineTo(-0.04314, 0.00577)
loop_1 = loop_1.threePointArc((-0.03902, -2e-05), (-0.03479, -0.0061))
loop_1 = loop_1.threePointArc((-0.03178, -0.0146), (-0.02917, -0.02225))
loop_1 = loop_1.lineTo(-0.02988, -0.03659)
loop_1 = loop_1.threePointArc((-0.03528, -0.04682), (-0.03955, -0.0533))
loop_1 = loop_1.lineTo(-0.04914, -0.06372)
loop_1 = loop_1.lineTo(-0.05964, -0.07277)
loop_1 = loop_1.lineTo(-0.06236, -0.0866)
loop_1 = loop_1.threePointArc((-0.06239, -0.03048), (-0.06241, 0.02667))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_3_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_3_interval_1.stl')