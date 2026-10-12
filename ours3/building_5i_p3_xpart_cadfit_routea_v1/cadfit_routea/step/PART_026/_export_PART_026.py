import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.99), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04843, -0.00762)
loop_1 = loop_1.lineTo(-0.04435, -0.01824)
loop_1 = loop_1.threePointArc((-0.03412, -0.03233), (-0.02927, -0.03667))
loop_1 = loop_1.lineTo(-0.0192, -0.04145)
loop_1 = loop_1.lineTo(0.00017, -0.0562)
loop_1 = loop_1.threePointArc((0.00085, -0.06164), (0.0014, -0.06731))
loop_1 = loop_1.threePointArc((0.01522, -0.07484), (0.02, -0.0739))
loop_1 = loop_1.lineTo(0.02655, -0.05663)
loop_1 = loop_1.threePointArc((0.0281, -0.04401), (0.03042, -0.04084))
loop_1 = loop_1.threePointArc((0.03587, -0.03454), (0.04077, -0.02839))
loop_1 = loop_1.lineTo(0.04851, 0.00282)
loop_1 = loop_1.lineTo(0.0449, 0.01372)
loop_1 = loop_1.threePointArc((0.03929, 0.02566), (0.03744, 0.02795))
loop_1 = loop_1.threePointArc((0.03149, 0.03525), (0.02893, 0.03817))
loop_1 = loop_1.threePointArc((0.02614, 0.04742), (0.02652, 0.05275))
loop_1 = loop_1.threePointArc((0.02604, 0.06722), (0.02376, 0.07203))
loop_1 = loop_1.lineTo(0.0046, 0.07148)
loop_1 = loop_1.lineTo(0.00022, 0.0516)
loop_1 = loop_1.lineTo(-0.01052, 0.0395)
loop_1 = loop_1.threePointArc((-0.02508, 0.03347), (-0.02944, 0.03105))
loop_1 = loop_1.lineTo(-0.04477, 0.01163)
loop_1 = loop_1.threePointArc((-0.04834, -0.00295), (-0.04842, -0.00749))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.97)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_026/PART_026.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_026/PART_026_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
