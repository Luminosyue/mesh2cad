import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.06, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.64499, -0.35004)
loop_1 = loop_1.lineTo(0.64948, -0.36697)
loop_1 = loop_1.lineTo(0.65385, -0.37814)
loop_1 = loop_1.lineTo(0.6589, -0.39234)
loop_1 = loop_1.lineTo(0.65981, -0.40914)
loop_1 = loop_1.lineTo(0.65829, -0.43487)
loop_1 = loop_1.threePointArc((0.65454, -0.45181), (0.65135, -0.46045))
loop_1 = loop_1.lineTo(0.6463, -0.48594)
loop_1 = loop_1.lineTo(0.64499, -0.35013)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_67_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_67_interval_0.stl')