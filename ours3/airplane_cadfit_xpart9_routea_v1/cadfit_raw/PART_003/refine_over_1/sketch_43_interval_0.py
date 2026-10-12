import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.92386, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02015, -0.02468)
loop_1 = loop_1.lineTo(0.02863, -0.04181)
loop_1 = loop_1.lineTo(0.04361, -0.07388)
loop_1 = loop_1.threePointArc((0.04996, -0.08781), (0.05634, -0.10088))
loop_1 = loop_1.lineTo(0.07739, -0.13529)
loop_1 = loop_1.threePointArc((0.08692, -0.14496), (0.09105, -0.14795))
loop_1 = loop_1.lineTo(0.11799, -0.16863)
loop_1 = loop_1.threePointArc((0.12332, -0.16985), (0.12869, -0.17127))
loop_1 = loop_1.lineTo(0.02015, -0.17104)
loop_1 = loop_1.lineTo(0.02015, -0.02483)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.55)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_43_interval_0.stl')