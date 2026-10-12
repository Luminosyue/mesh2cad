import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.07308), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16632, -0.69365)
loop_1 = loop_1.lineTo(-0.14811, -0.69335)
loop_1 = loop_1.lineTo(-0.1454, -0.68332)
loop_1 = loop_1.lineTo(-0.13866, -0.65166)
loop_1 = loop_1.lineTo(-0.13711, -0.64124)
loop_1 = loop_1.lineTo(-0.14846, -0.63527)
loop_1 = loop_1.lineTo(-0.16189, -0.63809)
loop_1 = loop_1.lineTo(-0.16758, -0.65275)
loop_1 = loop_1.threePointArc((-0.16848, -0.66302), (-0.16947, -0.67371))
loop_1 = loop_1.lineTo(-0.16632, -0.69365)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_44_interval_0.stl')