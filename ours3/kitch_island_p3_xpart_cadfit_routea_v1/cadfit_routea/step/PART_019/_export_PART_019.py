import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.00027, 0.00413, -0.00302), normal=(1.0, -0.0016, 0.00098), xDir=(-0.0016, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04954, 0.02515)
loop_1 = loop_1.lineTo(-0.05966, 0.00707)
loop_1 = loop_1.threePointArc((-0.05966, -0.00238), (-0.05972, -0.01222))
loop_1 = loop_1.lineTo(-0.04737, -0.02741)
loop_1 = loop_1.threePointArc((-0.0375, -0.0275), (-0.02802, -0.02746))
loop_1 = loop_1.threePointArc((-0.01492, -0.0276), (-0.0044, -0.02753))
loop_1 = loop_1.threePointArc((0.01837, -0.02766), (0.03857, -0.02755))
loop_1 = loop_1.lineTo(0.05921, -0.02153)
loop_1 = loop_1.lineTo(0.06169, -0.01048)
loop_1 = loop_1.threePointArc((0.06171, -0.00039), (0.06157, 0.0093))
loop_1 = loop_1.lineTo(0.05661, 0.02181)
loop_1 = loop_1.lineTo(0.04556, 0.02487)
loop_1 = loop_1.threePointArc((0.03587, 0.02488), (0.02578, 0.02503))
loop_1 = loop_1.threePointArc((0.00572, 0.02495), (-0.01337, 0.02507))
loop_1 = loop_1.lineTo(-0.0422, 0.02504)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_019/PART_019.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_019/PART_019_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
