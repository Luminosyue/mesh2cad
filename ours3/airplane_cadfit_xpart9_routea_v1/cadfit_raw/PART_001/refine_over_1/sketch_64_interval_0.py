import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.38992, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34471, -0.09629)
loop_1 = loop_1.lineTo(-0.56869, -0.10691)
loop_1 = loop_1.threePointArc((-0.62824, -0.10981), (-0.68493, -0.11322))
loop_1 = loop_1.lineTo(-0.79845, -0.11887)
loop_1 = loop_1.threePointArc((-0.85504, -0.12125), (-0.91353, -0.12318))
loop_1 = loop_1.threePointArc((-0.92349, -0.12283), (-0.93329, -0.12149))
loop_1 = loop_1.lineTo(-0.95206, -0.11308)
loop_1 = loop_1.threePointArc((-0.95622, -0.10785), (-0.95942, -0.1022))
loop_1 = loop_1.lineTo(-0.95909, -0.16608)
loop_1 = loop_1.lineTo(-0.34471, -0.16466)
loop_1 = loop_1.lineTo(-0.34471, -0.09675)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.7)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_64_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_64_interval_0.stl')