import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.36114, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.972, 0.10192)
loop_1 = loop_1.lineTo(-0.96693, 0.06104)
loop_1 = loop_1.lineTo(-0.95126, 0.04805)
loop_1 = loop_1.lineTo(-0.95124, -0.07228)
loop_1 = loop_1.lineTo(-0.94942, -0.08879)
loop_1 = loop_1.lineTo(-0.91306, -0.05822)
loop_1 = loop_1.lineTo(-0.90277, -0.05428)
loop_1 = loop_1.lineTo(-0.90571, -0.00289)
loop_1 = loop_1.lineTo(-0.95207, 0.0503)
loop_1 = loop_1.lineTo(-0.96664, 0.08645)
loop_1 = loop_1.lineTo(-0.97197, 0.10174)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.64)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_51_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_51_interval_0.stl')