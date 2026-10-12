import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.34604, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.83728, -0.2552)
loop_1 = loop_1.lineTo(0.83639, 0.14187)
loop_1 = loop_1.lineTo(0.79614, 0.04883)
loop_1 = loop_1.lineTo(0.77442, 0.02514)
loop_1 = loop_1.lineTo(0.74341, 0.00055)
loop_1 = loop_1.lineTo(0.74696, -0.05453)
loop_1 = loop_1.lineTo(0.7733, -0.06247)
loop_1 = loop_1.lineTo(0.81903, -0.09657)
loop_1 = loop_1.lineTo(0.8193, -0.07061)
loop_1 = loop_1.lineTo(0.8242, -0.10104)
loop_1 = loop_1.lineTo(0.834, -0.16454)
loop_1 = loop_1.threePointArc((0.8356, -0.19001), (0.83684, -0.21624))
loop_1 = loop_1.lineTo(0.83714, -0.2512)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_59_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_59_interval_1.stl')