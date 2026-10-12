import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.72168, -0.49729, -0.01819), normal=(-0.86978, 0.49324, 0.014), xDir=(0.49329, 0.86986, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.34404, 0.21822)
loop_1 = loop_1.lineTo(0.32576, -0.19182)
loop_1 = loop_1.lineTo(-0.32615, -0.19182)
loop_1 = loop_1.lineTo(-0.34902, -0.17884)
loop_1 = loop_1.lineTo(-0.37184, -0.19182)
loop_1 = loop_1.lineTo(-0.38148, -0.1722)
loop_1 = loop_1.lineTo(-0.39181, -0.17208)
loop_1 = loop_1.lineTo(-0.3945, -0.1589)
loop_1 = loop_1.threePointArc((-0.39676, -0.09668), (-0.39809, -0.03184))
loop_1 = loop_1.lineTo(-0.39938, -0.01492)
loop_1 = loop_1.lineTo(-0.40389, 0.13059)
loop_1 = loop_1.lineTo(-0.403, 0.1708)
loop_1 = loop_1.lineTo(-0.39004, 0.20742)
loop_1 = loop_1.lineTo(0.33283, 0.21822)
loop_1 = loop_1.lineTo(0.34404, 0.21822)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.72)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_6_interval_0.stl')