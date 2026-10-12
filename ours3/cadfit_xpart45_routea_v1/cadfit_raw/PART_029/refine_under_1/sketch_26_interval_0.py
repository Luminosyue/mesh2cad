import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.34304, -0.06703, 0.0774), normal=(-0.0365, 0.8948, 0.44498), xDir=(0.99917, 0.04075, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.31365, 0.29224)
loop_1 = loop_1.lineTo(-1.09306, 0.29224)
loop_1 = loop_1.lineTo(-1.10095, 0.25546)
loop_1 = loop_1.lineTo(-1.31339, 0.27493)
loop_1 = loop_1.lineTo(-1.31324, 0.28807)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_26_interval_0.stl')