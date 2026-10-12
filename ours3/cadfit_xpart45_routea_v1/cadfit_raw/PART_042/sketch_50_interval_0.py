import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.23782, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.62706, 0.35818)
loop_1 = loop_1.lineTo(-0.64231, 0.35004)
loop_1 = loop_1.lineTo(-0.65232, 0.34234)
loop_1 = loop_1.lineTo(-0.67213, 0.32932)
loop_1 = loop_1.lineTo(-0.66704, 0.31408)
loop_1 = loop_1.lineTo(-0.63332, 0.29488)
loop_1 = loop_1.lineTo(-0.60585, 0.2966)
loop_1 = loop_1.lineTo(-0.59577, 0.29778)
loop_1 = loop_1.lineTo(-0.5805, 0.30171)
loop_1 = loop_1.lineTo(-0.56723, 0.31497)
loop_1 = loop_1.threePointArc((-0.56652, 0.32021), (-0.56597, 0.32526))
loop_1 = loop_1.lineTo(-0.56794, 0.33593)
loop_1 = loop_1.lineTo(-0.58321, 0.35995)
loop_1 = loop_1.lineTo(-0.6091, 0.36583)
loop_1 = loop_1.lineTo(-0.62706, 0.35818)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.4)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_50_interval_0.stl')