import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.59748, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.25533, 0.25546)
loop_1 = loop_1.threePointArc((0.40543, 0.2534), (0.56117, 0.23937))
loop_1 = loop_1.threePointArc((0.70878, 0.20275), (0.84681, 0.12816))
loop_1 = loop_1.threePointArc((0.87821, 0.10811), (0.90705, 0.08465))
loop_1 = loop_1.threePointArc((0.91884, 0.06375), (0.91988, 0.04048))
loop_1 = loop_1.lineTo(0.91081, -0.07539)
loop_1 = loop_1.threePointArc((0.90775, -0.09333), (0.90213, -0.10986))
loop_1 = loop_1.lineTo(0.89173, -0.13171)
loop_1 = loop_1.threePointArc((0.83469, -0.17998), (0.76136, -0.20042))
loop_1 = loop_1.threePointArc((0.71596, -0.19609), (0.67198, -0.18259))
loop_1 = loop_1.threePointArc((0.59409, -0.13929), (0.52684, -0.07822))
loop_1 = loop_1.lineTo(0.44712, -0.01307)
loop_1 = loop_1.threePointArc((0.37185, 0.02479), (0.29383, 0.04029))
loop_1 = loop_1.threePointArc((0.28629, 0.04195), (0.28045, 0.04142))
loop_1 = loop_1.threePointArc((0.23411, 0.0461), (0.19094, 0.04319))
loop_1 = loop_1.threePointArc((0.17659, 0.04181), (0.16316, 0.04102))
loop_1 = loop_1.threePointArc((0.14048, 0.03552), (0.12066, 0.0288))
loop_1 = loop_1.lineTo(0.07625, 0.02094)
loop_1 = loop_1.threePointArc((0.0508, 0.01812), (0.02565, 0.01701))
loop_1 = loop_1.threePointArc((0.01071, 0.01519), (-0.00347, 0.01628))
loop_1 = loop_1.threePointArc((-0.06823, 0.01636), (-0.13353, 0.02448))
loop_1 = loop_1.threePointArc((-0.14549, 0.02825), (-0.15611, 0.02904))
loop_1 = loop_1.threePointArc((-0.17553, 0.03396), (-0.19313, 0.0365))
loop_1 = loop_1.threePointArc((-0.23357, 0.04237), (-0.271, 0.04033))
loop_1 = loop_1.threePointArc((-0.37965, 0.04008), (-0.48237, 0.03801))
loop_1 = loop_1.lineTo(-0.49429, 0.03779)
loop_1 = loop_1.lineTo(-0.55837, 0.03252)
loop_1 = loop_1.lineTo(-0.57558, 0.02572)
loop_1 = loop_1.threePointArc((-0.58965, 0.01815), (-0.60376, 0.01266))
loop_1 = loop_1.lineTo(-0.63845, -0.00402)
loop_1 = loop_1.lineTo(-0.68329, -0.02053)
loop_1 = loop_1.threePointArc((-0.70602, -0.02637), (-0.72884, -0.03061))
loop_1 = loop_1.threePointArc((-0.77864, -0.03172), (-0.82794, -0.02158))
loop_1 = loop_1.threePointArc((-0.88671, 0.01419), (-0.92686, 0.07155))
loop_1 = loop_1.threePointArc((-0.94395, 0.14447), (-0.95709, 0.21967))
loop_1 = loop_1.lineTo(-0.95127, 0.23384)
loop_1 = loop_1.threePointArc((-0.94023, 0.2432), (-0.92819, 0.24964))
loop_1 = loop_1.threePointArc((-0.72727, 0.25167), (-0.52624, 0.2505))
loop_1 = loop_1.threePointArc((-0.2109, 0.25281), (0.0903, 0.25651))
loop_1 = loop_1.threePointArc((0.17464, 0.25575), (0.25416, 0.25615))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.19)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/coast_guard_boat_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_003/PART_003.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/coast_guard_boat_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_003/PART_003_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
