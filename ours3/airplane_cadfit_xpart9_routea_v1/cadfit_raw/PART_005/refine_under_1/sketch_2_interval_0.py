import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.06752, -0.06872, -0.05703), normal=(-0.86817, 0.10861, 0.48423), xDir=(0.12413, 0.99227, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.4553, -0.05339)
loop_1 = loop_1.lineTo(-0.36781, -0.06129)
loop_1 = loop_1.lineTo(-0.30973, -0.06123)
loop_1 = loop_1.lineTo(-0.25346, -0.0577)
loop_1 = loop_1.lineTo(-0.21829, -0.05339)
loop_1 = loop_1.lineTo(-0.45294, -0.05339)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_2_interval_0.stl')