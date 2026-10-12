import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.97), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.06644, -0.17887)
loop_1 = loop_1.lineTo(-0.03932, -0.21528)
loop_1 = loop_1.threePointArc((0.00299, -0.21764), (0.03795, -0.21578))
loop_1 = loop_1.threePointArc((0.05392, -0.19529), (0.066, -0.1786))
loop_1 = loop_1.lineTo(0.06641, -0.0821)
loop_1 = loop_1.lineTo(0.06646, -0.01771)
loop_1 = loop_1.lineTo(0.0661, 0.18069)
loop_1 = loop_1.lineTo(0.04138, 0.2164)
loop_1 = loop_1.threePointArc((0.01502, 0.21935), (-0.006, 0.21942))
loop_1 = loop_1.lineTo(-0.03475, 0.21845)
loop_1 = loop_1.lineTo(-0.06603, 0.17939)
loop_1 = loop_1.threePointArc((-0.06562, 0.1444), (-0.06594, 0.10831))
loop_1 = loop_1.threePointArc((-0.06568, 0.06295), (-0.06595, 0.01608))
loop_1 = loop_1.lineTo(-0.06581, -0.10286)
loop_1 = loop_1.threePointArc((-0.06591, -0.1401), (-0.06649, -0.17852))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.95)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_002/PART_002.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_002/PART_002_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
