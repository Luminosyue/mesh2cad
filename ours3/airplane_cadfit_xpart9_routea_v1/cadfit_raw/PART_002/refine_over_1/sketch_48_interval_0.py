import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.01635, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.98293, -0.19529)
loop_1 = loop_1.threePointArc((-0.98322, -0.19), (-0.98322, -0.18447))
loop_1 = loop_1.lineTo(-0.98321, -0.17432)
loop_1 = loop_1.lineTo(-0.98267, -0.04539)
loop_1 = loop_1.lineTo(-0.917, -0.0456)
loop_1 = loop_1.lineTo(-0.92599, -0.05846)
loop_1 = loop_1.threePointArc((-0.93164, -0.06477), (-0.93751, -0.07117))
loop_1 = loop_1.lineTo(-0.98289, -0.19518)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_48_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_48_interval_0.stl')