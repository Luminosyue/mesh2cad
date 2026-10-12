import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.40792, -0.20659, 0.02629), normal=(-1.0, -0.0, 0.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.72117, 0.319)
loop_1 = loop_1.threePointArc((0.64718, 0.31842), (0.5701, 0.31852))
loop_1 = loop_1.threePointArc((0.45605, 0.31833), (0.35156, 0.31797))
loop_1 = loop_1.threePointArc((0.40621, 0.31744), (0.45729, 0.3175))
loop_1 = loop_1.threePointArc((0.48835, 0.31717), (0.51547, 0.31656))
loop_1 = loop_1.threePointArc((0.56029, 0.31472), (0.60171, 0.31237))
loop_1 = loop_1.threePointArc((0.62873, 0.3122), (0.64986, 0.31207))
loop_1 = loop_1.lineTo(0.69001, 0.31419)
loop_1 = loop_1.lineTo(0.73816, 0.31081)
loop_1 = loop_1.lineTo(0.75749, 0.30799)
loop_1 = loop_1.lineTo(0.77068, 0.30677)
loop_1 = loop_1.lineTo(0.7863, 0.30442)
loop_1 = loop_1.lineTo(0.82736, 0.30631)
loop_1 = loop_1.lineTo(0.86448, 0.31288)
loop_1 = loop_1.threePointArc((0.83329, 0.3131), (0.80396, 0.31628))
loop_1 = loop_1.lineTo(0.76012, 0.31827)
loop_1 = loop_1.lineTo(0.7268, 0.31891)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_2_interval_0.stl')