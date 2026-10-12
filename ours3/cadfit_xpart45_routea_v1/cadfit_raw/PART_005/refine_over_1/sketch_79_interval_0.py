import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.4827, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.97551, -0.44301)
loop_1 = loop_1.threePointArc((0.97611, -0.40675), (0.97759, -0.369))
loop_1 = loop_1.threePointArc((0.97727, -0.29211), (0.97823, -0.21253))
loop_1 = loop_1.lineTo(0.97731, -0.15261)
loop_1 = loop_1.lineTo(0.97325, -0.10653)
loop_1 = loop_1.lineTo(0.96272, -0.08884)
loop_1 = loop_1.threePointArc((0.9453, -0.07304), (0.9278, -0.05663))
loop_1 = loop_1.lineTo(0.95445, 0.0508)
loop_1 = loop_1.lineTo(0.97697, 0.13368)
loop_1 = loop_1.lineTo(0.98051, 0.14596)
loop_1 = loop_1.lineTo(0.97882, 0.13491)
loop_1 = loop_1.lineTo(0.97739, -0.53018)
loop_1 = loop_1.lineTo(0.9664, -0.53018)
loop_1 = loop_1.threePointArc((0.97352, -0.49326), (0.97548, -0.46644))
loop_1 = loop_1.lineTo(0.97551, -0.44348)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.91)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_79_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_79_interval_0.stl')