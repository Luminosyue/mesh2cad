import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.53625, 0.60024, 0.06693), normal=(0.62223, 0.78284, 0.0), xDir=(0.78284, -0.62223, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.48086, -0.02734)
loop_1 = loop_1.lineTo(0.49141, -0.04344)
loop_1 = loop_1.lineTo(0.49621, -0.09674)
loop_1 = loop_1.lineTo(0.49471, -0.40064)
loop_1 = loop_1.lineTo(0.49184, -0.42147)
loop_1 = loop_1.lineTo(0.48761, -0.44264)
loop_1 = loop_1.lineTo(0.4822, -0.46326)
loop_1 = loop_1.lineTo(0.47628, -0.02587)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_0_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_0_interval_1.stl')