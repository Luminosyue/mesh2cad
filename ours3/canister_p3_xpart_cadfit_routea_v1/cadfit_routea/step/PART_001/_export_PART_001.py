import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01522, -0.07343, 0.00106), normal=(-1e-05, 1.0, 2e-05), xDir=(1.0, 1e-05, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.41561, 0.99379)
loop_1 = loop_1.threePointArc((0.38618, 0.99383), (0.35797, 0.99242))
loop_1 = loop_1.lineTo(-0.12062, 0.99365)
loop_1 = loop_1.lineTo(-0.13593, 0.99364)
loop_1 = loop_1.lineTo(-0.30879, 0.99265)
loop_1 = loop_1.lineTo(-0.3256, 0.9935)
loop_1 = loop_1.lineTo(-0.62214, 0.99241)
loop_1 = loop_1.threePointArc((-0.72234, 0.98717), (-0.80964, 0.97383))
loop_1 = loop_1.threePointArc((-0.84924, 0.95867), (-0.88047, 0.94176))
loop_1 = loop_1.lineTo(-0.89058, 0.93035)
loop_1 = loop_1.lineTo(-0.90253, 0.92398)
loop_1 = loop_1.lineTo(-0.92945, 0.89773)
loop_1 = loop_1.threePointArc((-0.97378, 0.8251), (-0.99865, 0.75881))
loop_1 = loop_1.lineTo(-1.00068, 0.74662)
loop_1 = loop_1.threePointArc((-1.01304, 0.60141), (-1.01371, 0.4615))
loop_1 = loop_1.lineTo(-1.0127, -0.60961)
loop_1 = loop_1.threePointArc((-1.00749, -0.68327), (-0.99917, -0.7463))
loop_1 = loop_1.threePointArc((-0.97603, -0.81654), (-0.94228, -0.8754))
loop_1 = loop_1.threePointArc((-0.89004, -0.92919), (-0.8347, -0.96048))
loop_1 = loop_1.threePointArc((-0.74162, -0.98082), (-0.65586, -0.98814))
loop_1 = loop_1.threePointArc((-0.496, -0.99133), (-0.35054, -0.98995))
loop_1 = loop_1.lineTo(-0.33994, -0.99072)
loop_1 = loop_1.lineTo(0.5994, -0.98967)
loop_1 = loop_1.threePointArc((0.70367, -0.98206), (0.79716, -0.96011))
loop_1 = loop_1.threePointArc((0.86462, -0.92209), (0.91356, -0.86927))
loop_1 = loop_1.threePointArc((0.95696, -0.7637), (0.97139, -0.66108))
loop_1 = loop_1.threePointArc((0.98191, -0.5417), (0.98239, -0.43331))
loop_1 = loop_1.threePointArc((0.98461, 0.08308), (0.98096, 0.57019))
loop_1 = loop_1.lineTo(0.96609, 0.7434)
loop_1 = loop_1.lineTo(0.95996, 0.7758)
loop_1 = loop_1.threePointArc((0.93769, 0.84336), (0.90517, 0.89424))
loop_1 = loop_1.threePointArc((0.85783, 0.93568), (0.81514, 0.95896))
loop_1 = loop_1.threePointArc((0.76888, 0.97582), (0.72596, 0.98238))
loop_1 = loop_1.threePointArc((0.58246, 0.99257), (0.45254, 0.99311))
loop_1 = loop_1.lineTo(0.41962, 0.99394)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/canister_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_001/PART_001.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/canister_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_001/PART_001_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
