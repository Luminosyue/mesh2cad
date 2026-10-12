import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.74897, -0.11605, 0.49992), normal=(0.83379, 0.00102, 0.55208), xDir=(0.00123, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.78943, 0.30151)
loop_1 = loop_1.lineTo(-0.8173, 0.2996)
loop_1 = loop_1.lineTo(-0.83265, 0.28646)
loop_1 = loop_1.lineTo(-0.53857, 0.28554)
loop_1 = loop_1.lineTo(-0.55478, 0.28701)
loop_1 = loop_1.lineTo(-0.57056, 0.28646)
loop_1 = loop_1.lineTo(-0.61391, 0.29008)
loop_1 = loop_1.lineTo(-0.63224, 0.28933)
loop_1 = loop_1.threePointArc((-0.66397, 0.29025), (-0.69393, 0.29142))
loop_1 = loop_1.lineTo(-0.7307, 0.29796)
loop_1 = loop_1.lineTo(-0.75561, 0.301)
loop_1 = loop_1.lineTo(-0.78635, 0.30146)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_12_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_12_interval_2.stl')