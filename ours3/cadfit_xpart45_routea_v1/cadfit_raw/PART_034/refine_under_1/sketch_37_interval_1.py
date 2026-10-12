import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.78033, 0.09455, 0.0491), normal=(0.96693, 0.25502, -0.00123), xDir=(0.25502, -0.96694, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.35617, 0.17565)
loop_1 = loop_1.lineTo(0.35686, -0.06156)
loop_1 = loop_1.lineTo(0.358, -0.03567)
loop_1 = loop_1.threePointArc((0.3582, -0.01436), (0.35795, 0.0039))
loop_1 = loop_1.threePointArc((0.36198, 0.06027), (0.36675, 0.10892))
loop_1 = loop_1.threePointArc((0.36616, 0.13509), (0.36537, 0.15788))
loop_1 = loop_1.lineTo(0.35727, 0.17354)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_37_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_37_interval_1.stl')