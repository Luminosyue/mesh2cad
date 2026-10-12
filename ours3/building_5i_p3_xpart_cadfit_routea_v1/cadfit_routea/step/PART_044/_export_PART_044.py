import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.21171, -0.26874)
loop_1 = loop_1.lineTo(-0.21051, -0.56618)
loop_1 = loop_1.lineTo(-0.20926, -0.57914)
loop_1 = loop_1.lineTo(-0.18916, -0.5819)
loop_1 = loop_1.threePointArc((-0.1494, -0.54746), (-0.11313, -0.51367))
loop_1 = loop_1.threePointArc((-0.05291, -0.46077), (0.00296, -0.40917))
loop_1 = loop_1.threePointArc((0.04713, -0.37134), (0.09375, -0.33432))
loop_1 = loop_1.threePointArc((0.14258, -0.29455), (0.19452, -0.25615))
loop_1 = loop_1.lineTo(0.20695, -0.24678)
loop_1 = loop_1.threePointArc((0.2104, -0.23618), (0.21089, -0.2265))
loop_1 = loop_1.lineTo(0.21024, 0.58153)
loop_1 = loop_1.lineTo(0.19971, 0.58711)
loop_1 = loop_1.threePointArc((-0.00767, 0.58751), (-0.20675, 0.58604))
loop_1 = loop_1.threePointArc((-0.21177, 0.50357), (-0.21131, 0.42728))
loop_1 = loop_1.lineTo(-0.21171, -0.26778)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.99)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_044/PART_044.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_044/PART_044_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
