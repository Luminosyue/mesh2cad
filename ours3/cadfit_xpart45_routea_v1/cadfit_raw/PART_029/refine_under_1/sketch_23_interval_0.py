import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.19377, 0.00741, 0.26237), normal=(-0.0, -0.78921, -0.61412), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.77327, 0.10368)
loop_1 = loop_1.threePointArc((-0.76594, 0.10325), (-0.7589, 0.10291))
loop_1 = loop_1.lineTo(-0.73673, 0.07301)
loop_1 = loop_1.threePointArc((-0.73617, 0.06617), (-0.73548, 0.05961))
loop_1 = loop_1.threePointArc((-0.73634, 0.04983), (-0.73739, 0.04508))
loop_1 = loop_1.lineTo(-0.79994, 0.06098)
loop_1 = loop_1.lineTo(-0.80327, 0.04876)
loop_1 = loop_1.lineTo(-0.80402, 0.07191)
loop_1 = loop_1.threePointArc((-0.79891, 0.08436), (-0.79439, 0.0923))
loop_1 = loop_1.lineTo(-0.77582, 0.10285)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_23_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_23_interval_0.stl')