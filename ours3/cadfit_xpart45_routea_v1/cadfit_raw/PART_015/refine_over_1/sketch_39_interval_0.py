import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.2164), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.77735, -0.46205)
loop_1 = loop_1.lineTo(-0.7771, -0.54208)
loop_1 = loop_1.lineTo(-0.71137, -0.5419)
loop_1 = loop_1.lineTo(-0.73205, -0.52033)
loop_1 = loop_1.lineTo(-0.75213, -0.49492)
loop_1 = loop_1.lineTo(-0.76929, -0.47376)
loop_1 = loop_1.lineTo(-0.77731, -0.46212)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_39_interval_0.stl')