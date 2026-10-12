import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.08479, -0.21533, -0.21323), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.98839, 0.63117)
loop_1 = loop_1.lineTo(1.00478, 0.60886)
loop_1 = loop_1.lineTo(1.0284, 0.57366)
loop_1 = loop_1.threePointArc((1.03654, 0.56066), (1.04424, 0.54817))
loop_1 = loop_1.lineTo(1.04425, 0.63271)
loop_1 = loop_1.lineTo(0.98836, 0.63271)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_21_interval_0.stl')