import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.42815, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.15314, 0.00048)
loop_1 = loop_1.lineTo(0.15262, -0.17)
loop_1 = loop_1.lineTo(0.02073, -0.16959)
loop_1 = loop_1.lineTo(0.04479, -0.13813)
loop_1 = loop_1.threePointArc((0.05279, -0.12671), (0.06114, -0.11505))
loop_1 = loop_1.threePointArc((0.06705, -0.10704), (0.07239, -0.09932))
loop_1 = loop_1.threePointArc((0.07891, -0.09049), (0.08589, -0.08168))
loop_1 = loop_1.threePointArc((0.09614, -0.06748), (0.10752, -0.05347))
loop_1 = loop_1.threePointArc((0.11233, -0.04759), (0.1174, -0.04176))
loop_1 = loop_1.lineTo(0.1288, -0.02765)
loop_1 = loop_1.lineTo(0.14817, -0.00697)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.4)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_35_interval_0.stl')