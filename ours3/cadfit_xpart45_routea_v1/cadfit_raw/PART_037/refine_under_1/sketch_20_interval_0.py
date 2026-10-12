import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.75474, -0.01006, -0.02907), normal=(0.0419, -0.01236, 0.99905), xDir=(-0.0, 0.99992, 0.01238))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07547, 0.66638)
loop_1 = loop_1.lineTo(-0.06963, 0.68042)
loop_1 = loop_1.lineTo(-0.02679, 0.7001)
loop_1 = loop_1.lineTo(-0.0087, 0.69277)
loop_1 = loop_1.lineTo(0.00256, 0.67815)
loop_1 = loop_1.lineTo(0.00542, 0.66608)
loop_1 = loop_1.lineTo(-0.00475, 0.69971)
loop_1 = loop_1.lineTo(-0.02948, 0.70737)
loop_1 = loop_1.threePointArc((-0.03532, 0.70732), (-0.04141, 0.7073))
loop_1 = loop_1.lineTo(-0.05649, 0.70115)
loop_1 = loop_1.lineTo(-0.07174, 0.68838)
loop_1 = loop_1.lineTo(-0.07547, 0.66638)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_20_interval_0.stl')