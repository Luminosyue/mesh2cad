import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02357, -0.43055, 0.07301), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.59139, -0.66179)
loop_1 = loop_1.lineTo(0.56628, -0.6759)
loop_1 = loop_1.lineTo(0.54341, -0.68843)
loop_1 = loop_1.lineTo(0.51512, -0.70499)
loop_1 = loop_1.lineTo(0.49889, -0.71418)
loop_1 = loop_1.lineTo(0.59357, -0.71418)
loop_1 = loop_1.lineTo(0.59357, -0.66136)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_30_interval_0.stl')