import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.21089, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.93803, 0.32827)
loop_1 = loop_1.lineTo(0.9179, 0.31699)
loop_1 = loop_1.lineTo(0.90542, 0.30623)
loop_1 = loop_1.threePointArc((0.89797, 0.29646), (0.89099, 0.28707))
loop_1 = loop_1.lineTo(0.89605, 0.26743)
loop_1 = loop_1.lineTo(0.91876, 0.25652)
loop_1 = loop_1.lineTo(0.94015, 0.2534)
loop_1 = loop_1.lineTo(0.9578, 0.25161)
loop_1 = loop_1.lineTo(0.97732, 0.26166)
loop_1 = loop_1.lineTo(0.99272, 0.28723)
loop_1 = loop_1.lineTo(0.98771, 0.30674)
loop_1 = loop_1.lineTo(0.97684, 0.31902)
loop_1 = loop_1.lineTo(0.96248, 0.32641)
loop_1 = loop_1.lineTo(0.93811, 0.32828)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/sketch_9_interval_0.stl')