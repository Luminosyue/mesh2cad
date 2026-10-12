import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.36487, 0.04481, -0.02316), normal=(-1.0, 0.0, 0.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.62548, 0.17179)
loop_1 = loop_1.lineTo(0.62548, -0.17718)
loop_1 = loop_1.lineTo(0.62915, -0.16549)
loop_1 = loop_1.threePointArc((0.62998, -0.14349), (0.63116, -0.12059))
loop_1 = loop_1.threePointArc((0.63034, -0.09453), (0.62962, -0.07248))
loop_1 = loop_1.threePointArc((0.63013, -0.03813), (0.63009, -0.00821))
loop_1 = loop_1.threePointArc((0.6291, 0.02931), (0.62912, 0.06471))
loop_1 = loop_1.threePointArc((0.62932, 0.09463), (0.62951, 0.11994))
loop_1 = loop_1.threePointArc((0.62803, 0.14643), (0.62671, 0.16804))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_50_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_50_interval_1.stl')