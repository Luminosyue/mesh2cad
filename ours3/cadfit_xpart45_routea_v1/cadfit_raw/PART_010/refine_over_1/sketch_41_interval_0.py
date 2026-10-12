import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.23458, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.43797, -0.58334)
loop_1 = loop_1.lineTo(0.34, -0.50656)
loop_1 = loop_1.lineTo(0.33937, -0.6689)
loop_1 = loop_1.lineTo(-0.49927, -0.66711)
loop_1 = loop_1.lineTo(-0.48474, -0.62627)
loop_1 = loop_1.lineTo(-0.47351, -0.60924)
loop_1 = loop_1.lineTo(-0.45084, -0.59003)
loop_1 = loop_1.threePointArc((-0.44457, -0.58666), (-0.43854, -0.58362))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_41_interval_0.stl')