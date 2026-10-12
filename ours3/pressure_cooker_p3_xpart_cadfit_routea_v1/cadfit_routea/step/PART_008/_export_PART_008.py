import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.13644, -0.11985, 0.11146), normal=(0.01792, -0.01954, -0.99965), xDir=(0.0, -0.99981, 0.01954))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00017, 0.87114)
loop_1 = loop_1.threePointArc((0.04997, 0.92226), (0.09567, 0.97362))
loop_1 = loop_1.lineTo(0.23075, 1.1035)
loop_1 = loop_1.threePointArc((0.25536, 1.12374), (0.27896, 1.13649))
loop_1 = loop_1.lineTo(0.30129, 1.13892)
loop_1 = loop_1.lineTo(0.32843, 1.13272)
loop_1 = loop_1.lineTo(0.35241, 1.12175)
loop_1 = loop_1.threePointArc((0.42108, 1.06312), (0.4776, 0.99637))
loop_1 = loop_1.threePointArc((0.55133, 0.89404), (0.60776, 0.78447))
loop_1 = loop_1.threePointArc((0.66495, 0.63312), (0.70423, 0.47197))
loop_1 = loop_1.threePointArc((0.72133, 0.30084), (0.70995, 0.12868))
loop_1 = loop_1.threePointArc((0.70045, 0.06332), (0.684, -0.00043))
loop_1 = loop_1.threePointArc((0.66424, -0.07401), (0.63891, -0.14328))
loop_1 = loop_1.threePointArc((0.60214, -0.22741), (0.56195, -0.30325))
loop_1 = loop_1.threePointArc((0.51842, -0.36807), (0.47287, -0.4317))
loop_1 = loop_1.threePointArc((0.39161, -0.51827), (0.30408, -0.59598))
loop_1 = loop_1.threePointArc((0.23739, -0.64963), (0.16518, -0.69742))
loop_1 = loop_1.threePointArc((0.10339, -0.73095), (0.04479, -0.76105))
loop_1 = loop_1.threePointArc((-0.10254, -0.8129), (-0.25641, -0.84497))
loop_1 = loop_1.threePointArc((-0.50979, -0.85461), (-0.76396, -0.80804))
loop_1 = loop_1.threePointArc((-0.83126, -0.78786), (-0.89069, -0.77141))
loop_1 = loop_1.threePointArc((-0.9295, -0.75599), (-0.96336, -0.73924))
loop_1 = loop_1.lineTo(-0.9688, -0.72412)
loop_1 = loop_1.threePointArc((-0.9366, -0.67652), (-0.89964, -0.62944))
loop_1 = loop_1.lineTo(-0.76846, -0.44033)
loop_1 = loop_1.threePointArc((-0.70503, -0.35212), (-0.65476, -0.26737))
loop_1 = loop_1.threePointArc((-0.61557, -0.18919), (-0.57287, -0.109))
loop_1 = loop_1.threePointArc((-0.52941, -0.02109), (-0.49338, 0.05602))
loop_1 = loop_1.threePointArc((-0.42635, 0.19292), (-0.36782, 0.31874))
loop_1 = loop_1.threePointArc((-0.32528, 0.41044), (-0.27511, 0.49666))
loop_1 = loop_1.threePointArc((-0.23701, 0.56497), (-0.19669, 0.62937))
loop_1 = loop_1.threePointArc((-0.13858, 0.70463), (-0.0783, 0.77791))
loop_1 = loop_1.threePointArc((-0.04113, 0.82399), (-0.00423, 0.86627))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/pressure_cooker_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_008/PART_008.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/pressure_cooker_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_008/PART_008_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
