import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.03573, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.2793, 0.00017)
loop_1 = loop_1.lineTo(0.20134, -0.07003)
loop_1 = loop_1.threePointArc((0.18011, -0.08613), (0.15793, -0.10258))
loop_1 = loop_1.lineTo(0.1469, -0.11)
loop_1 = loop_1.lineTo(0.2793, -0.10958)
loop_1 = loop_1.lineTo(0.2793, 3e-05)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_45_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_45_interval_0.stl')