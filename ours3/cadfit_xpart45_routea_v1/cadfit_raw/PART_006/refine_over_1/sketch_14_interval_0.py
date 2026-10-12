import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.1296, -0.07679, 0.42298), normal=(-0.80848, -0.00079, 0.58852), xDir=(-0.00098, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.43523, 0.04678)
loop_1 = loop_1.lineTo(0.46686, 0.03664)
loop_1 = loop_1.threePointArc((0.48983, 0.03085), (0.50893, 0.02625))
loop_1 = loop_1.threePointArc((0.53808, 0.0294), (0.56468, 0.03331))
loop_1 = loop_1.lineTo(0.61455, 0.05098)
loop_1 = loop_1.lineTo(0.64235, 0.02654)
loop_1 = loop_1.lineTo(0.65827, 0.01318)
loop_1 = loop_1.lineTo(0.66653, 0.00017)
loop_1 = loop_1.threePointArc((0.67878, -0.02528), (0.68986, -0.0473))
loop_1 = loop_1.threePointArc((0.69526, -0.05672), (0.69855, -0.06284))
loop_1 = loop_1.threePointArc((0.70947, -0.08324), (0.71848, -0.10095))
loop_1 = loop_1.threePointArc((0.72411, -0.11012), (0.72758, -0.11553))
loop_1 = loop_1.lineTo(0.46674, -0.11702)
loop_1 = loop_1.lineTo(0.46666, 0.03645)
loop_1 = loop_1.lineTo(0.4391, 0.04532)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_14_interval_0.stl')