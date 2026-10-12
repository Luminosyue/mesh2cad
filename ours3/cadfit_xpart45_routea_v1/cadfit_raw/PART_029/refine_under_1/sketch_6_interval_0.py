import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0739, 0.07102, 0.01381), normal=(0.03612, -0.89054, 0.45346), xDir=(-0.99918, -0.04053, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.57757, 0.02672)
loop_1 = loop_1.lineTo(-0.50464, 0.02672)
loop_1 = loop_1.threePointArc((-0.51236, 0.03785), (-0.5189, 0.04288))
loop_1 = loop_1.lineTo(-0.5334, 0.04681)
loop_1 = loop_1.lineTo(-0.54706, 0.04785)
loop_1 = loop_1.lineTo(-0.57757, 0.02672)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_6_interval_0.stl')