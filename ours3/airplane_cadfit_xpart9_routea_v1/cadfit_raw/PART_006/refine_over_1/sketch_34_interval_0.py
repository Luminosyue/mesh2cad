import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.80976, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.64468, 0.18779)
loop_1 = loop_1.lineTo(-0.59248, 0.1835)
loop_1 = loop_1.threePointArc((-0.50908, 0.1744), (-0.4229, 0.16319))
loop_1 = loop_1.lineTo(-0.38399, 0.15803)
loop_1 = loop_1.threePointArc((-0.35253, 0.15404), (-0.32271, 0.15083))
loop_1 = loop_1.threePointArc((-0.26675, 0.14401), (-0.21339, 0.13822))
loop_1 = loop_1.lineTo(-0.17073, 0.13291)
loop_1 = loop_1.lineTo(-0.71827, 0.28164)
loop_1 = loop_1.lineTo(-0.75407, 0.14826)
loop_1 = loop_1.lineTo(-0.73615, 0.16584)
loop_1 = loop_1.threePointArc((-0.72218, 0.17523), (-0.70659, 0.18326))
loop_1 = loop_1.threePointArc((-0.69017, 0.18811), (-0.67938, 0.18953))
loop_1 = loop_1.threePointArc((-0.66236, 0.18889), (-0.64514, 0.18781))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.64)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_34_interval_0.stl')