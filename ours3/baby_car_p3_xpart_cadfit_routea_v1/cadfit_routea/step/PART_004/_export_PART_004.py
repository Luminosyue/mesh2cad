import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.4), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.99732, 0.23231)
loop_1 = loop_1.threePointArc((-0.99437, 0.21166), (-0.98627, 0.19334))
loop_1 = loop_1.threePointArc((-0.96527, 0.14405), (-0.94565, 0.09379))
loop_1 = loop_1.threePointArc((-0.92393, 0.04311), (-0.90562, -0.00936))
loop_1 = loop_1.threePointArc((-0.88025, -0.06204), (-0.85265, -0.10844))
loop_1 = loop_1.threePointArc((-0.80221, -0.1826), (-0.74924, -0.24842))
loop_1 = loop_1.threePointArc((-0.70097, -0.30243), (-0.65053, -0.34799))
loop_1 = loop_1.threePointArc((-0.55953, -0.41637), (-0.46514, -0.46823))
loop_1 = loop_1.threePointArc((-0.39212, -0.48856), (-0.32104, -0.48954))
loop_1 = loop_1.threePointArc((0.02654, -0.48655), (0.38667, -0.48485))
loop_1 = loop_1.threePointArc((0.43023, -0.47982), (0.46926, -0.46984))
loop_1 = loop_1.threePointArc((0.49242, -0.45851), (0.51239, -0.44674))
loop_1 = loop_1.threePointArc((0.59784, -0.38861), (0.67257, -0.32608))
loop_1 = loop_1.threePointArc((0.75452, -0.24794), (0.82184, -0.1644))
loop_1 = loop_1.threePointArc((0.89109, -0.04757), (0.93998, 0.07168))
loop_1 = loop_1.threePointArc((0.97969, 0.19808), (0.99959, 0.32216))
loop_1 = loop_1.lineTo(0.99763, 0.35962)
loop_1 = loop_1.threePointArc((0.98443, 0.3852), (0.96911, 0.40634))
loop_1 = loop_1.lineTo(0.94963, 0.41788)
loop_1 = loop_1.threePointArc((0.92287, 0.42485), (0.89812, 0.4271))
loop_1 = loop_1.threePointArc((0.85391, 0.43059), (0.81293, 0.43015))
loop_1 = loop_1.threePointArc((0.69114, 0.43014), (0.56622, 0.43587))
loop_1 = loop_1.threePointArc((0.54372, 0.43751), (0.52329, 0.44515))
loop_1 = loop_1.threePointArc((0.48887, 0.45506), (0.45623, 0.45587))
loop_1 = loop_1.lineTo(0.32843, 0.45727)
loop_1 = loop_1.threePointArc((0.27943, 0.45205), (0.2343, 0.44504))
loop_1 = loop_1.lineTo(0.11955, 0.44281)
loop_1 = loop_1.threePointArc((0.07167, 0.44212), (0.0237, 0.44566))
loop_1 = loop_1.threePointArc((-0.03728, 0.44258), (-0.09897, 0.44288))
loop_1 = loop_1.lineTo(-0.13454, 0.44725)
loop_1 = loop_1.threePointArc((-0.17306, 0.44253), (-0.2081, 0.43615))
loop_1 = loop_1.threePointArc((-0.24844, 0.43297), (-0.28879, 0.43233))
loop_1 = loop_1.threePointArc((-0.40124, 0.44669), (-0.5079, 0.45668))
loop_1 = loop_1.threePointArc((-0.59317, 0.44458), (-0.66986, 0.41879))
loop_1 = loop_1.threePointArc((-0.69791, 0.4096), (-0.72565, 0.40143))
loop_1 = loop_1.lineTo(-0.85291, 0.3917)
loop_1 = loop_1.threePointArc((-0.89627, 0.38666), (-0.93568, 0.37839))
loop_1 = loop_1.lineTo(-0.95544, 0.36861)
loop_1 = loop_1.lineTo(-0.96607, 0.35786)
loop_1 = loop_1.lineTo(-0.98061, 0.32631)
loop_1 = loop_1.threePointArc((-0.98749, 0.28395), (-0.99697, 0.2419))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.81)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/baby_car_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_004/PART_004.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/baby_car_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_004/PART_004_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
