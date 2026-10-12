import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.58), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.9574, -0.03026)
loop_1 = loop_1.lineTo(-0.95331, -0.09743)
loop_1 = loop_1.threePointArc((-0.937, -0.19324), (-0.91526, -0.28197))
loop_1 = loop_1.threePointArc((-0.88146, -0.36904), (-0.84515, -0.44883))
loop_1 = loop_1.threePointArc((-0.77195, -0.56832), (-0.69277, -0.67465))
loop_1 = loop_1.threePointArc((-0.61812, -0.74041), (-0.54462, -0.7981))
loop_1 = loop_1.threePointArc((-0.43282, -0.86619), (-0.31908, -0.91504))
loop_1 = loop_1.threePointArc((-0.23795, -0.94366), (-0.1589, -0.95973))
loop_1 = loop_1.threePointArc((0.06843, -0.97109), (0.28173, -0.93272))
loop_1 = loop_1.threePointArc((0.43498, -0.86716), (0.56682, -0.77969))
loop_1 = loop_1.threePointArc((0.63925, -0.72428), (0.70091, -0.6649))
loop_1 = loop_1.threePointArc((0.76614, -0.59269), (0.81544, -0.51568))
loop_1 = loop_1.threePointArc((0.86893, -0.42071), (0.90901, -0.32613))
loop_1 = loop_1.threePointArc((0.92894, -0.25624), (0.94553, -0.19051))
loop_1 = loop_1.threePointArc((0.95198, -0.13609), (0.95553, -0.08559))
loop_1 = loop_1.threePointArc((0.96281, -0.02019), (0.96391, 0.04099))
loop_1 = loop_1.lineTo(0.937, 0.21498)
loop_1 = loop_1.threePointArc((0.92626, 0.26101), (0.91239, 0.30216))
loop_1 = loop_1.threePointArc((0.81694, 0.50399), (0.68982, 0.67433))
loop_1 = loop_1.threePointArc((0.65204, 0.71082), (0.61477, 0.74186))
loop_1 = loop_1.threePointArc((0.47813, 0.82989), (0.33964, 0.89734))
loop_1 = loop_1.lineTo(0.26416, 0.91846)
loop_1 = loop_1.threePointArc((0.17905, 0.94013), (0.0982, 0.95559))
loop_1 = loop_1.threePointArc((-0.07139, 0.9561), (-0.2298, 0.92822))
loop_1 = loop_1.threePointArc((-0.36911, 0.88357), (-0.49269, 0.82086))
loop_1 = loop_1.threePointArc((-0.58297, 0.75914), (-0.66349, 0.69482))
loop_1 = loop_1.threePointArc((-0.70136, 0.65676), (-0.73283, 0.61852))
loop_1 = loop_1.threePointArc((-0.77746, 0.56419), (-0.81389, 0.50974))
loop_1 = loop_1.threePointArc((-0.86908, 0.39806), (-0.91208, 0.2885))
loop_1 = loop_1.threePointArc((-0.92478, 0.23832), (-0.93226, 0.19116))
loop_1 = loop_1.threePointArc((-0.94803, 0.10287), (-0.95705, 0.01924))
loop_1 = loop_1.threePointArc((-0.95718, -0.00598), (-0.95734, -0.02828))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.62)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/fire_truck_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_000/PART_000.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/fire_truck_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_000/PART_000_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
