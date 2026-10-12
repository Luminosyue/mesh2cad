import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.47082, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.81787, 0.51411)
loop_1 = loop_1.lineTo(-0.82461, 0.46197)
loop_1 = loop_1.lineTo(-0.83094, 0.40828)
loop_1 = loop_1.lineTo(-0.83397, 0.36142)
loop_1 = loop_1.lineTo(-0.83753, 0.30755)
loop_1 = loop_1.lineTo(-0.8374, 0.51982)
loop_1 = loop_1.lineTo(-0.81553, 0.51982)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_71_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_71_interval_1.stl')