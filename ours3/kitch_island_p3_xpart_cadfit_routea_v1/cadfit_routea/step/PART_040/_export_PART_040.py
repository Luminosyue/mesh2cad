import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.98, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00932, 0.5265)
loop_1 = loop_1.lineTo(0.00209, 0.52259)
loop_1 = loop_1.threePointArc((0.01099, 0.51417), (0.01788, 0.50439))
loop_1 = loop_1.lineTo(0.02542, 0.48822)
loop_1 = loop_1.lineTo(0.02666, 0.45708)
loop_1 = loop_1.lineTo(0.02482, -0.48899)
loop_1 = loop_1.threePointArc((0.01862, -0.50434), (0.0085, -0.51765))
loop_1 = loop_1.threePointArc((-0.00491, -0.52499), (-0.00932, -0.52613))
loop_1 = loop_1.lineTo(-0.01989, -0.52016)
loop_1 = loop_1.threePointArc((-0.02527, -0.50408), (-0.02507, -0.49285))
loop_1 = loop_1.threePointArc((-0.02467, 0.02221), (-0.02517, 0.51594))
loop_1 = loop_1.threePointArc((-0.01447, 0.52409), (-0.00998, 0.52618))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_040/PART_040.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_040/PART_040_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
