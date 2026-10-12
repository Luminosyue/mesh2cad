import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.46903, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.81685, 0.51417)
loop_1 = loop_1.lineTo(-0.8286, 0.46206)
loop_1 = loop_1.lineTo(-0.83246, 0.40853)
loop_1 = loop_1.lineTo(-0.83494, 0.35421)
loop_1 = loop_1.lineTo(-0.8356, 0.32955)
loop_1 = loop_1.lineTo(-0.83512, 0.51982)
loop_1 = loop_1.lineTo(-0.81353, 0.51982)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_64_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_64_interval_1.stl')