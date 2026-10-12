import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2463, 0.80978, -0.04933), normal=(0.32593, -0.94536, 0.0075), xDir=(-0.94539, -0.32594, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.21722, 0.18287)
loop_1 = loop_1.lineTo(-0.20558, 0.16922)
loop_1 = loop_1.lineTo(-0.18265, 0.12594)
loop_1 = loop_1.lineTo(-0.17846, 0.11286)
loop_1 = loop_1.lineTo(-0.18028, -0.15714)
loop_1 = loop_1.lineTo(-0.41863, -0.15714)
loop_1 = loop_1.lineTo(-0.42084, 0.11371)
loop_1 = loop_1.lineTo(-0.41443, 0.12605)
loop_1 = loop_1.lineTo(-0.37111, 0.16922)
loop_1 = loop_1.lineTo(-0.35792, 0.17704)
loop_1 = loop_1.lineTo(-0.34735, 0.18287)
loop_1 = loop_1.lineTo(-0.22279, 0.18287)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.58)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_9_interval_0.stl')