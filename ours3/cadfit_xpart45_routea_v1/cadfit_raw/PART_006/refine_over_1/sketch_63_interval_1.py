import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.53164, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34381, -0.41228)
loop_1 = loop_1.lineTo(-0.35933, -0.42534)
loop_1 = loop_1.threePointArc((-0.37715, -0.45288), (-0.39632, -0.48021))
loop_1 = loop_1.lineTo(-0.4387, -0.52936)
loop_1 = loop_1.lineTo(0.48594, -0.5275)
loop_1 = loop_1.threePointArc((0.47394, -0.51312), (0.46251, -0.49834))
loop_1 = loop_1.lineTo(0.44696, -0.47129)
loop_1 = loop_1.lineTo(0.42194, -0.42237)
loop_1 = loop_1.lineTo(0.02965, -0.41448)
loop_1 = loop_1.threePointArc((0.08606, -0.41366), (0.13945, -0.41244))
loop_1 = loop_1.lineTo(-0.19839, -0.41174)
loop_1 = loop_1.threePointArc((-0.2337, -0.41071), (-0.26945, -0.4064))
loop_1 = loop_1.threePointArc((-0.28085, -0.40503), (-0.29177, -0.40265))
loop_1 = loop_1.threePointArc((-0.31835, -0.40741), (-0.34307, -0.41212))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_63_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_63_interval_1.stl')