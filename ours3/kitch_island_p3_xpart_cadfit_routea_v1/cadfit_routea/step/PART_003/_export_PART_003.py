import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.97), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07505, -0.17419)
loop_1 = loop_1.lineTo(-0.06855, -0.21422)
loop_1 = loop_1.lineTo(-0.04004, -0.23853)
loop_1 = loop_1.lineTo(0.00526, -0.23933)
loop_1 = loop_1.lineTo(0.03934, -0.23836)
loop_1 = loop_1.lineTo(0.06666, -0.21357)
loop_1 = loop_1.lineTo(0.07506, -0.17262)
loop_1 = loop_1.lineTo(0.07499, -0.04196)
loop_1 = loop_1.threePointArc((0.07516, 0.01347), (0.07462, 0.06631))
loop_1 = loop_1.threePointArc((0.0749, 0.12753), (0.07436, 0.18593))
loop_1 = loop_1.lineTo(0.06562, 0.2236)
loop_1 = loop_1.lineTo(0.03865, 0.24461)
loop_1 = loop_1.threePointArc((-0.00222, 0.24491), (-0.04106, 0.24425))
loop_1 = loop_1.lineTo(-0.06716, 0.22294)
loop_1 = loop_1.lineTo(-0.07442, 0.18157)
loop_1 = loop_1.threePointArc((-0.0747, 0.07214), (-0.07461, -0.03253))
loop_1 = loop_1.lineTo(-0.07485, -0.15259)
loop_1 = loop_1.lineTo(-0.07504, -0.1738)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.94)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_003/PART_003.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_003/PART_003_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
