import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.24748, -0.15278, 0.17933), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.17293, 0.74975)
loop_1 = loop_1.lineTo(-0.17293, 0.68951)
loop_1 = loop_1.lineTo(-0.18617, 0.70534)
loop_1 = loop_1.lineTo(-0.21107, 0.72548)
loop_1 = loop_1.lineTo(-0.2444, 0.74051)
loop_1 = loop_1.lineTo(-0.27995, 0.74975)
loop_1 = loop_1.lineTo(-0.17439, 0.74975)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_12_interval_0.stl')