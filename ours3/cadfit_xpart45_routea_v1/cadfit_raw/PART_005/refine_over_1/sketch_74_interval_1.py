import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.32931, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.86076, 0.15151)
loop_1 = loop_1.lineTo(-0.84902, 0.0985)
loop_1 = loop_1.threePointArc((-0.84512, 0.08883), (-0.84121, 0.07984))
loop_1 = loop_1.lineTo(-0.82613, 0.0474)
loop_1 = loop_1.lineTo(-0.8009, 0.01649)
loop_1 = loop_1.lineTo(-0.78157, -0.00398)
loop_1 = loop_1.lineTo(-0.78322, -0.03561)
loop_1 = loop_1.lineTo(-0.78648, -0.05567)
loop_1 = loop_1.lineTo(-0.79986, -0.06095)
loop_1 = loop_1.lineTo(-0.82945, -0.0787)
loop_1 = loop_1.lineTo(-0.85181, -0.10183)
loop_1 = loop_1.lineTo(-0.86076, -0.14363)
loop_1 = loop_1.lineTo(-0.86076, 0.15129)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.13)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_74_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_74_interval_1.stl')